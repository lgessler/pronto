import os
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


def construct_dataset_dict(tsv_path, integer_label, max_integer_label):
    insts = []
    with open(tsv_path, "r") as f:
        for line in f:
            l = line.strip()
            if "\t" in l:
                text, label = l.split("\t")
                if integer_label:
                    label = int(label)
                    label = label if label < max_integer_label else max_integer_label
                insts.append({"text": text, "label": label})
    seed(42)
    shuffle(insts)

    dataset = datasets.Dataset.from_list(insts)
    ddict = dataset.train_test_split(test_size=0.2)
    ddict2 = ddict["test"].train_test_split(test_size=0.5)
    ddict["dev"] = ddict2["train"]
    ddict["test"] = ddict2["test"]
    ddict.features = datasets.Features(
        {
            "text": Sequence(feature=Value(dtype="string", id=None), length=-1, id=None),
            "label": Sequence(feature=ClassLabel(names=list(set(dataset["label"])), id=None), length=-1, id=None),
        }
    )
    return ddict


def evaluate_model(
    model_name,
    tsv_path,
    output_dir=None,
    integer_label=False,
    max_integer_label=None,
    lr=3e-5,
):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    dataset_dict = construct_dataset_dict(tsv_path, integer_label, max_integer_label)

    tokenized_dataset_dict = dataset_dict.map(lambda x: tokenizer(x["text"], truncation=True), batched=True)
    collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="pt")

    accuracy = evaluate.load("accuracy")

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        return accuracy.compute(predictions=predictions, references=labels)

    possible_labels = dataset_dict.features["label"].feature.names
    label2id = {v: i for i, v in enumerate(possible_labels)}
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(possible_labels),
        id2label={i: v for i, v in enumerate(possible_labels)},
        label2id=label2id,
    )

    if output_dir is None:
        output_dir = gettempdir() + os.sep + f"{tsv_path.replace(os.sep, '_')}__{model_name}"

    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=lr,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=20,
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
    eval_results = task_evaluator.compute(
        model_or_pipeline=model, data=dataset_dict["test"], label_mapping=label2id, tokenizer=tokenizer
    )
    return eval_results


@click.command
@click.argument("model_name")
@click.argument("tsv_path")
@click.option("-o", "--output-dir", default=None)
@click.option("--integer-label/--no-integer-label", default=False, help="Set to true if labels are integers")
@click.option("--max-integer-label", default=None, type=int, help="Maximum value for labels if they are integers")
@click.option("--lr", default=3e-5, type=float, help="Learning rate")
def run(
    model_name,
    tsv_path,
    output_dir,
    integer_label,
    max_integer_label,
    lr,
):
    print(evaluate_model(**locals()))


if __name__ == "__main__":
    run()
