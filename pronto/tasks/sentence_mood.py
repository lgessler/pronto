from logging import getLogger
from pathlib import Path
from typing import List

from pronto.aligning import AlignedVerse
from pronto.tasks._util import train_dev_test_split
from pronto.tasks.spec import TaskSpec

logger = getLogger(__name__)


def process_verse(verse):
    first_sentence = verse.ontonotes_sentences[0]
    parsed_tree = first_sentence.tree.parsed_tree
    stype = parsed_tree[0].label()
    # Attested values are: {'S-IMP', 'SINV', 'SBAR-PRP', 'XX', 'S', 'NP', 'FRAG',
    #                       'X', 'SQ', 'SBARQ', 'S-CLF', 'INTJ', 'SBAR', 'PRN', '``', 'NP-VOC'}
    # For meanings, see https://www.ldc.upenn.edu/sites/www.ldc.upenn.edu/files/penn-etb-2-style-guidelines.pdf
    if stype in ["S", "S-CLF"]:
        stype = "declarative"
    elif stype in ["S-IMP"]:
        stype = "imperative"
    elif stype in ["SQ", "SBARQ", "SQ-CLF"]:
        stype = "interrogative"
    else:
        return None

    return verse.verse.body, stype


def process_verses(verses, output_dir):
    outputs = []
    for i, verse in enumerate(verses):
        if not verse.is_cross_verse:
            output = process_verse(verse)
            if output is not None:
                outputs.append(output)

    for split, rows in zip(["train", "dev", "test"], train_dev_test_split(outputs)):
        with open(Path(output_dir) / Path(f"sentence_mood_{split}.tsv"), "w") as f:
            for s, l in rows:
                f.write(f"{s}\t{l}\n")


@TaskSpec.register("sentence_mood")
class SentenceMood(TaskSpec):
    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        process_verses(verses, output_dir)
