from collections import defaultdict
from logging import getLogger
from pathlib import Path
from typing import List

from stanza import Pipeline

from pronto.aligning import AlignedVerse
from pronto.tasks._util import token_yield_of_tree_node, train_dev_test_split
from pronto.tasks.spec import TaskSpec

logger = getLogger(__name__)


def is_contiguous(indexes):
    if len(indexes) == 0:
        return True
    for i in range(1, len(indexes)):
        if indexes[i - 1] != indexes[i] - 1:
            return False
    return True


def process_verse(verse, pipeline):
    first_sentence = verse.ontonotes_sentences[0]
    parsed_tree = first_sentence.tree.parsed_tree
    subject_tokens = token_yield_of_tree_node(parsed_tree, "NP-SBJ")
    if len(subject_tokens) == 0:
        logger.debug(f"Couldn't find a subject for verse: {(verse.book, verse.chapter, verse.verse_id)}")
        return None
    if not is_contiguous([x[0] for x in subject_tokens]):
        logger.warning(
            f"Skipping verse because subject token indices were not contiguous: {(verse.book, verse.chapter, verse.verse_id)}"
        )
        return None

    output = pipeline(verse.verse.body)
    sentence = output.sentences[0].to_dict()
    word_index = {w["id"]: w for w in sentence if isinstance(w["id"], int)}
    head_map = {w["id"]: w["head"] for w in sentence if isinstance(w["id"], int)}

    nsubj = [w for w in sentence if w["deprel"] == "nsubj"]
    if len(nsubj) == 0:
        return verse.verse.body, 0
    elif nsubj[0]["upos"] == "PROPN":
        return verse.verse.body, 1
    else:
        prev_children = [nsubj[0]]

    while True:
        next_children = [w for w, h in head_map.items() if h in prev_children]
        if len(next_children) == 0:
            break
        if any(word_index[w]["upos"] == "PROPN" for w in next_children):
            return verse.verse.body, 1
        prev_children = next_children

    return verse.verse.body, 0


def process_verses(verses, output_dir, pipeline):
    outputs = []
    for verse in verses:
        if not verse.is_cross_verse:
            output = process_verse(verse, pipeline)
            if output is not None:
                outputs.append(output)
    with open(Path(output_dir) / Path(f"ud_proper_noun_subject.tsv"), "w") as f:
        for s, c in outputs:
            f.write(f"{s}\t{c}\n")
    for split, rows in zip(["train", "dev", "test"], train_dev_test_split(outputs)):
        with open(Path(output_dir) / Path(f"ud_proper_noun_subject_{split}.tsv"), "w") as f:
            for s, c in rows:
                f.write(f"{s}\t{c}\n")


@TaskSpec.register("ud_proper_noun_subject")
class UdProperNounSubject(TaskSpec):
    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        pipeline = Pipeline(lang="hi")
        process_verses(verses, output_dir, pipeline)
