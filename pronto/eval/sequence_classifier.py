import os
from logging import getLogger
from tempfile import gettempdir

import click
import datasets
import evaluate
import numpy as np
from datasets import ClassLabel, Value
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer,
                          TrainingArguments)

logger = getLogger(__name__)


def construct_dataset_dict(
    tsv_base_path,
    integer_label,
    max_integer_label,
    text_column_index,
    label_column_index,
    second_text_column_index,
    extra_input_column_index,
):
    def read_tsv(tsv_path):
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
        return insts

    train_insts = read_tsv(tsv_base_path + "_train.tsv")
    dev_insts = read_tsv(tsv_base_path + "_dev.tsv")
    test_insts = read_tsv(tsv_base_path + "_test.tsv")

    all_labels = sorted(list(set([x["label"] for xs in [train_insts, dev_insts, test_insts] for x in xs])))
    features = {"text": Value(dtype="string", id=None), "label": ClassLabel(names=all_labels, id=None)}
    if second_text_column_index is not None:
        features["text2"] = Value(dtype="string", id=None)
    if extra_input_column_index is not None:
        all_extras = sorted(list(set([x["extra"] for xs in [train_insts, dev_insts, test_insts] for x in xs])))
        features["extra"] = ClassLabel(names=all_extras, id=None)
    features = datasets.Features(features)

    ddict = {
        "train": datasets.Dataset.from_list(train_insts, features=features),
        "dev": datasets.Dataset.from_list(dev_insts, features=features),
        "test": datasets.Dataset.from_list(test_insts, features=features),
    }
    ddict = datasets.DatasetDict(ddict)
    return ddict


def evaluate_model(
    model_name,
    tsv_base_path,
    output_dir=None,
    integer_label=False,
    max_integer_label=None,
    num_proc=4,
    lr=2e-5,
    batch_size=16,
    epochs=10,
    text_column_index=0,
    label_column_index=1,
    second_text_column_index=None,
    extra_input_column_index=None,
    max_sequence_length=512,
):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    dataset_dict = construct_dataset_dict(
        tsv_base_path,
        integer_label,
        max_integer_label,
        text_column_index,
        label_column_index,
        second_text_column_index,
        extra_input_column_index,
    )
    possible_labels = dataset_dict["train"].features["label"].names
    label2id = {v: i for i, v in enumerate(possible_labels)}
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(possible_labels),
        id2label={i: v for i, v in enumerate(possible_labels)},
        label2id=label2id,
    )

    if extra_input_column_index is not None:
        extras = dataset_dict["train"].features["extra"].names
        tokenizer.add_tokens(extras)
        model.resize_token_embeddings(len(tokenizer))

    def tokenize(batch):
        args = [batch["text"]]
        if second_text_column_index is not None:
            args.append(batch["text2"])
        tokenizer_outputs = tokenizer(*args, truncation=True, max_length=max_sequence_length)
        if extra_input_column_index is not None:
            extra_ids = [tokenizer.vocab[extras[x]] for x in batch["extra"]]
            for k, vs in tokenizer_outputs.items():
                for i, v in enumerate(vs):
                    if len(v) == max_sequence_length:
                        v.pop(-1)
                    v.append(extra_ids[i] if k == "input_ids" else 1)
        return tokenizer_outputs

    tokenized_dataset_dict = dataset_dict.map(tokenize, batched=True, batch_size=batch_size, num_proc=num_proc)
    collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")

    accuracy = evaluate.load("accuracy")

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        return accuracy.compute(predictions=predictions, references=labels)

    if output_dir is None:
        output_dir = gettempdir() + os.sep + f"{tsv_base_path.replace(os.sep, '_')}__{model_name}"

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

    predictions = trainer.predict(tokenized_dataset_dict["test"])
    test_acc = accuracy.compute(
        predictions=predictions.predictions.argmax(-1), references=tokenized_dataset_dict["test"]["label"]
    )
    return {"accuracy": test_acc, "predictions": predictions, "test_instances": tokenized_dataset_dict["test"]}


@click.command
@click.argument("model_name")
@click.argument("tsv_base_path")
@click.option("-o", "--output-dir", default=None)
@click.option("--integer-label/--no-integer-label", default=False, help="Set to true if labels are integers")
@click.option("--max-integer-label", default=None, type=int, help="Maximum value for labels if they are integers")
@click.option("--num-proc", default=4, type=int, help="Processors to use for dataset mapping")
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
    tsv_base_path,
    output_dir,
    integer_label,
    max_integer_label,
    num_proc,
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
