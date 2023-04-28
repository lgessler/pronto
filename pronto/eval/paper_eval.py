import json

from pronto.eval.sequence_classifier import evaluate_model

MULTI_MODELS = ["bert-base-multilingual-cased", "xlm-roberta-base", "xlm-roberta-large"]
MODELS = {
    "ind": ["lgessler/microbert-indonesian-m", "lgessler/microbert-indonesian-mx", "cahya/bert-base-indonesian-522M"],
    "tam2017": [
        "lgessler/microbert-tamil-m",
        "lgessler/microbert-tamil-mx",
        "l3cube-pune/tamil-bert",
    ],
    "copshc": [
        "lgessler/microbert-coptic-m",
        "lgessler/microbert-coptic-mx",
    ],
    "uigara": [
        "lgessler/microbert-uyghur-m",
        "lgessler/microbert-uyghur-mx",
    ],
    "grcmt": [
        "lgessler/microbert-ancient-greek-m",
        "lgessler/microbert-ancient-greek-mx",
    ],
    "wolKYG": [
        "lgessler/microbert-wolof-m",
        "lgessler/microbert-wolof-mx",
    ],
    "frasbl": ["camembert-base"],
    "jpn1965": ["cl-tohoku/bert-base-japanese"],
    "engwebster": [
        "roberta-base",
        "bert-base-cased",
        "distilbert-base-cased",
    ],
    "engerv": [
        "roberta-base",
        "bert-base-cased",
        "distilbert-base-cased",
    ],
}


def run_sentence_mood(bible, model, task):
    if model in MULTI_MODELS:
        return evaluate_model(
            model, f"output/{bible}/{task}", epochs=20, num_proc=12, batch_size=8, gradient_accumulation_steps=2
        )
    else:
        return evaluate_model(model, f"output/{bible}/{task}", epochs=20, num_proc=12)


def run_nonpronominal_mention(bible, model, task):
    if model in MULTI_MODELS:
        return evaluate_model(
            model,
            f"output/{bible}/{task}",
            epochs=10,
            integer_label=True,
            max_integer_label=3,
            num_proc=12,
            batch_size=8,
            gradient_accumulation_steps=2,
        )
    else:
        return evaluate_model(
            model, f"output/{bible}/{task}", epochs=10, integer_label=True, max_integer_label=3, num_proc=12
        )


def run_proper_noun_subject(bible, model, task):
    if model in MULTI_MODELS:
        return evaluate_model(
            model, f"output/{bible}/{task}", epochs=10, num_proc=12, batch_size=8, gradient_accumulation_steps=2
        )
    else:
        return evaluate_model(model, f"output/{bible}/{task}", epochs=10, num_proc=12)


def run_same_sense(bible, model, task):
    if model in MULTI_MODELS:
        return evaluate_model(
            model,
            f"output/{bible}/{task}",
            epochs=10,
            text_column_index=1,
            second_text_column_index=2,
            extra_input_column_index=0,
            label_column_index=3,
            num_proc=12,
            batch_size=8,
            gradient_accumulation_steps=2,
        )
    else:
        return evaluate_model(
            model,
            f"output/{bible}/{task}",
            epochs=10,
            text_column_index=1,
            second_text_column_index=2,
            extra_input_column_index=0,
            label_column_index=3,
            num_proc=12,
        )


def run_same_arg_count(bible, model, task):
    if model in MULTI_MODELS:
        return evaluate_model(
            model,
            f"output/{bible}/{task}",
            epochs=10,
            text_column_index=1,
            second_text_column_index=2,
            extra_input_column_index=0,
            label_column_index=3,
            num_proc=12,
            batch_size=8,
            gradient_accumulation_steps=2,
        )
    else:
        return evaluate_model(
            model,
            f"output/{bible}/{task}",
            epochs=10,
            text_column_index=1,
            second_text_column_index=2,
            extra_input_column_index=0,
            label_column_index=3,
            num_proc=12,
        )


TASKS = {
    "nonpronominal_mention": run_nonpronominal_mention,
    "proper_noun_subject": run_proper_noun_subject,
    "same_sense": run_same_sense,
    "sentence_mood": run_sentence_mood,
    "same_arg_count": run_same_arg_count,
}


def run_trial(bible, model, task):
    with open("results.tsv", "r") as f:
        if "\t".join([bible, model, task]) in f.read():
            return
    print(f"Running {bible}-{model}-{task}")
    result = TASKS[task](bible, model, task)
    with open("results.tsv", "a") as f:
        f.write("\t".join([bible, model, task, str(result["accuracy"]["accuracy"])]) + "\n")
    with open(f"preds/{bible}-{model.replace('/', '_')}-{task}.json", "w") as f:
        predictions = result["predictions"]
        result["predictions"] = predictions.predictions.argmax(-1).tolist()
        result["gold_label_ids"] = predictions.label_ids.tolist()
        result["metrics"] = predictions.metrics
        result["test_instances"] = [x for x in result["test_instances"]]
        f.write(json.dumps(result))


def run():
    for bible, models in MODELS.items():
        for task in TASKS.keys():
            for model in models:
                run_trial(bible, model, task)
    for bible in MODELS.keys():
        for task in TASKS.keys():
            for model in MULTI_MODELS:
                run_trial(bible, model, task)


if __name__ == "__main__":
    run()
