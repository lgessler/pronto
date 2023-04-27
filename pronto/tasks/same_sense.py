import random
from collections import Counter, defaultdict
from logging import getLogger
from pathlib import Path
from typing import List

from pronto.aligning import AlignedVerse
from pronto.tasks._util import train_dev_test_split
from pronto.tasks.spec import TaskSpec

logger = getLogger(__name__)


def build_index(config, verses: List[AlignedVerse]):
    # mapping from sense labels to verses which contain them
    index = defaultdict(list)

    for verse in verses:
        sense_annotations = []
        for sentence in verse.ontonotes_sentences:
            for leaf in sentence.leaves:
                if leaf.prop is not None:
                    sense_annotations.append(leaf.prop)

        # if we only want verses with a single sense annotation, bail out
        if config.singleton_only and len(sense_annotations) != 1:
            continue

        if not config.allow_duplicate_senses_in_verse and len(set(s.label for s in sense_annotations)) != len(
            sense_annotations
        ):
            continue

        for sense in sense_annotations:
            if verse not in index[sense.label]:
                index[sense.label].append(verse)

    return index


def process_verses(
    config,
    verses,
    output_dir,
):
    random.seed(42)
    index = build_index(config, verses)
    outputs = []

    for label, verses in index.items():
        other_sense_keys = [x for x in index.keys() if x != label]
        # All verses for other sense labels. Note that we also exclude verses which contain `label`.
        other_sense_verses = [v for x in other_sense_keys for v in index[x] if v not in verses]
        for i, verse in enumerate(verses):

            def sample(vs, n, positive=True):
                if len(vs) == 0:
                    if i == 0 and positive:
                        logger.warning(f"Sense {label} had only one instance!")
                    return []
                elif len(vs) < n:
                    if i == 0 and positive:
                        logger.warning(f"Sense {label} had only {len(vs) + 1} instances!")
                    n = len(vs)
                return random.sample(vs, n)

            # Candidates for same sense pairings: everything after this one (avoid duplicate combinations)
            same_sense_verses = verses[i + 1 :]
            positive_examples = sample(same_sense_verses, config.positive_pairs_per_instance)
            negative_examples = sample(
                other_sense_verses, min(config.negative_per_positive * len(positive_examples), len(positive_examples))
            )
            for verse2 in positive_examples:
                outputs.append((label, verse.verse.body, verse2.verse.body, "same"))
            for verse2 in negative_examples:
                outputs.append((label, verse.verse.body, verse2.verse.body, "different"))

    for split, rows in zip(["train", "dev", "test"], train_dev_test_split(outputs)):
        with open(Path(output_dir) / Path(f"same_sense_{split}.tsv"), "w") as f:
            for sense, s1, s2, l in rows:
                f.write(f"{sense}\t{s1}\t{s2}\t{l}\n")


@TaskSpec.register("same_sense")
class SameSense(TaskSpec):
    def __init__(
        self,
        singleton_only: bool = False,
        allow_duplicate_senses_in_verse: bool = True,
        negative_per_positive: int = 1,
        positive_pairs_per_instance: int = 1,
    ):
        self.singleton_only = singleton_only
        self.allow_duplicate_senses_in_verse = allow_duplicate_senses_in_verse
        self.negative_per_positive = negative_per_positive
        self.positive_pairs_per_instance = positive_pairs_per_instance

    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        process_verses(
            self,
            verses,
            output_dir,
        )
