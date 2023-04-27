import os
from logging import getLogger
from random import seed, shuffle
from tempfile import gettempdir

import click
import datasets
import evaluate
import numpy as np
from datasets import ClassLabel, Sequence, Value
from evaluate import evaluator
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer,
                          TrainingArguments)

logger = getLogger(__name__)


def construct_dataset_dict(
    tsv_path,
    integer_label,
    max_integer_label,
    text_column_index,
    label_column_index,
    second_text_column_index,
    extra_input_column_index,
):
    insts = []
    with open(tsv_path, "r") as f:
        for line in f:
            l = line.strip()
            if "\t" in l:
                pieces = l.split("\t")
                text = pieces[text_column_index]
                label = pieces[label_column_index]
                if integer_label:
                    label = int(label)
                    label = label if label < max_integer_label else max_integer_label
                output = {"text": text, "label": label}
                if second_text_column_index is not None:
                    output["text2"] = pieces[second_text_column_index]
                if extra_input_column_index is not None:
                    output["extra"] = pieces[extra_input_column_index]
                insts.append(output)
    seed(42)
    shuffle(insts)

    dataset = datasets.Dataset.from_list(insts)
    ddict = dataset.train_test_split(test_size=0.2)
    ddict2 = ddict["test"].train_test_split(test_size=0.5)
    ddict["dev"] = ddict2["train"]
    ddict["test"] = ddict2["test"]
    features = {
        "text": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
        "label": Sequence(feature=ClassLabel(names=list(set(dataset["label"])), id=None), length=-1, id=None),
    }
    if second_text_column_index is not None:
        features["text2"] = Sequence(feature=Value(dtype="string", id=None), length=-1, id=None)
    if extra_input_column_index is not None:
        features["extra"] = Sequence(feature=ClassLabel(names=list(set(dataset["extra"])), id=None), length=-1, id=None)

    ddict.features = datasets.Features(features)
    return ddict


def evaluate_model(
    model_name,
    tsv_path,
    output_dir=None,
    integer_label=False,
    max_integer_label=None,
    lr=3e-5,
    batch_size=16,
    epochs=10,
    text_column_index=0,
    label_column_index=1,
    second_text_column_index=None,
    extra_input_column_index=None,
    max_sequence_length=None,
):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    dataset_dict = construct_dataset_dict(
        tsv_path,
        integer_label,
        max_integer_label,
        text_column_index,
        label_column_index,
        second_text_column_index,
        extra_input_column_index,
    )
    possible_labels = dataset_dict.features["label"].feature.names
    label2id = {v: i for i, v in enumerate(possible_labels)}
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(possible_labels),
        id2label={i: v for i, v in enumerate(possible_labels)},
        label2id=label2id,
    )

    if extra_input_column_index is not None:
        extras = dataset_dict.features["extra"].feature.names
        tokenizer.add_tokens(extras)
        model.resize_token_embeddings(len(tokenizer))

    def tokenize(batch):
        args = [batch["text"]]
        if second_text_column_index is not None:
            args.append(batch["text2"])
        tokenizer_outputs = tokenizer(*args, truncation=True, max_length=max_sequence_length)
        if extra_input_column_index is not None:
            extra_ids = [tokenizer.vocab[x] for x in batch["extra"]]
            for k, vs in tokenizer_outputs.items():
                for i, v in enumerate(vs):
                    if len(v) == max_sequence_length:
                        v.pop(-1)
                    v.append(extra_ids[i] if k == "input_ids" else 1)
        return tokenizer_outputs

    tokenized_dataset_dict = dataset_dict.map(tokenize, batched=True, batch_size=batch_size)
    if not integer_label:
        tokenized_dataset_dict = tokenized_dataset_dict.map(lambda x: {"label": label2id[x["label"]]})
    collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")

    accuracy = evaluate.load("accuracy")

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        return accuracy.compute(predictions=predictions, references=labels)

    if output_dir is None:
        output_dir = gettempdir() + os.sep + f"{tsv_path.replace(os.sep, '_')}__{model_name}"

    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=lr,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset_dict["train"],
        eval_dataset=tokenized_dataset_dict["dev"],
        tokenizer=tokenizer,
        data_collator=collator,
        compute_metrics=compute_metrics,
    )
    trainer.train()

    task_evaluator = evaluator("text-classification")
    test_dataset = dataset_dict["test"]
    if not integer_label:
        test_dataset = test_dataset.map(lambda x: {"label": label2id[x["label"]]})
    eval_results = task_evaluator.compute(
        model_or_pipeline=model, data=test_dataset, label_mapping=label2id, tokenizer=tokenizer
    )
    return eval_results


@click.command
@click.argument("model_name")
@click.argument("tsv_path")
@click.option("-o", "--output-dir", default=None)
@click.option("--integer-label/--no-integer-label", default=False, help="Set to true if labels are integers")
@click.option("--max-integer-label", default=None, type=int, help="Maximum value for labels if they are integers")
@click.option("--lr", default=3e-5, type=float, help="Learning rate")
@click.option("--batch-size", default=16, type=int, help="Batch size")
@click.option("--epochs", default=10, type=int, help="Number of training epochs")
@click.option("--text-column-index", default=0, type=int, help="TSV column which contains text")
@click.option("--label-column-index", default=1, type=int, help="TSV column which contains sequence label")
@click.option(
    "--second-text-column-index",
    default=None,
    type=int,
    help="TSV column which contains second sequence, if applicable",
)
@click.option("--extra-input-column-index", default=None, type=int, help="See use in code")
@click.option("--max-sequence-length", default=512, type=int)
def run(
    model_name,
    tsv_path,
    output_dir,
    integer_label,
    max_integer_label,
    lr,
    batch_size,
    epochs,
    text_column_index,
    label_column_index,
    second_text_column_index,
    extra_input_column_index,
    max_sequence_length,
):
    print(evaluate_model(**locals()))


if __name__ == "__main__":
    run()
