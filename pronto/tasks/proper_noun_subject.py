from logging import getLogger
from pathlib import Path
from typing import List

from pronto.aligning import AlignedVerse
from pronto.tasks._util import token_yield_of_tree_node
from pronto.tasks.spec import TaskSpec

logger = getLogger(__name__)


def is_contiguous(indexes):
    if len(indexes) == 0:
        return True
    for i in range(1, len(indexes)):
        if indexes[i - 1] != indexes[i] - 1:
            return False
    return True


def process_verse(verse, subject_tag):
    first_sentence = verse.ontonotes_sentences[0]
    parsed_tree = first_sentence.tree.parsed_tree
    subject_tokens = token_yield_of_tree_node(parsed_tree, subject_tag)
    if len(subject_tokens) == 0:
        logger.warning(f"Couldn't find a subject for verse: {(verse.book, verse.chapter, verse.verse_id)}")
        return None
    if not is_contiguous([x[0] for x in subject_tokens]):
        logger.warning(
            f"Skipping verse because subject token indices were not contiguous: {(verse.book, verse.chapter, verse.verse_id)}"
        )
        return None

    subject_is_proper_noun = any(t[1][-1] == "NNP" for t in subject_tokens)
    return verse.verse.body, 1 if subject_is_proper_noun else 0


def process_verses(verses, output_dir, subject_tag):
    outputs = []
    for i, verse in enumerate(verses):
        if not verse.is_cross_verse:
            output = process_verse(verse, subject_tag)
            if output is not None:
                outputs.append(output)
    with open(Path(output_dir) / Path("proper_noun_subject.tsv"), "w") as f:
        for s, l in outputs:
            f.write(f"{s}\t{l}\n")


@TaskSpec.register("proper_noun_subject")
class ProperNounSubject(TaskSpec):
    def __init__(self, subject_tag: str = "NP-SBJ"):
        self.subject_tag = subject_tag

    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        process_verses(verses, output_dir, self.subject_tag)
