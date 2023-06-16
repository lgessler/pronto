from pathlib import Path
from typing import List

from stanza import Pipeline

from pronto.aligning import AlignedVerse
from pronto.tasks._util import train_dev_test_split
from pronto.tasks.spec import TaskSpec


def process_verse(verse, pipeline):
    output = pipeline(verse.verse.body)

    mentions = 0
    for token in output.iter_tokens():
        for word in token.words:
            word = word.to_dict()
            if (
                "upos" in word
                and word["upos"] in ["PROPN", "NOUN"]
                and not (word["upos"] == "NOUN" and word["deprel"] == "compound")
            ):
                mentions += 1

    return verse.verse.body, mentions, verse.reference


def process_verses(verses, output_dir, pipeline):
    outputs = []
    for verse in verses:
        if not verse.is_cross_verse:
            outputs.append(process_verse(verse, pipeline))
    with open(Path(output_dir) / Path(f"ud_nonpronominal_mention.tsv"), "w") as f:
        for s, c, r in outputs:
            f.write(f"{s}\t{c}\t{r}\n")
    for split, rows in zip(["train", "dev", "test"], train_dev_test_split(outputs)):
        with open(Path(output_dir) / Path(f"ud_nonpronominal_mention_{split}.tsv"), "w") as f:
            for s, c, r in rows:
                f.write(f"{s}\t{c}\t{r}\n")


@TaskSpec.register("ud_nonpronominal_mention")
class UdNonpronominalMention(TaskSpec):
    VERSION = "C"

    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        pipeline = Pipeline(lang="hi")
        process_verses(verses, output_dir, pipeline)
