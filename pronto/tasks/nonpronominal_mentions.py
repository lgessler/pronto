import re
from pathlib import Path
from typing import List

from onf_parser import Mention

from pronto.aligning import AlignedVerse
from pronto.tasks.spec import TaskSpec

PRONOUN_PATTERN = re.compile(
    r"i|me|my|mine|myself"
    r"|we|our|ours|ourselves"
    r"|thou|thy|thine|thyself"
    r"|you|your|yours|yourself|yourselves"
    r"|he|him|his|himself"
    r"|she|her|hers|herself"
    r"|it|its|itself"
    r"|they|them|their|theirs|themself|themselves",
    flags=re.IGNORECASE,
)


def is_pronominal(mention: Mention):
    # Discard null tokens
    tokens = [t for t in mention.tokens if "*" not in t]
    return len(tokens) == 1 and re.match(PRONOUN_PATTERN, tokens[0]) is not None


def process_verse(verse):
    mentions = 0
    for mention in verse.mentions:
        if not is_pronominal(mention):
            mentions += 1
    return verse.verse.body, mentions


def process_verses(verses, output_dir):
    outputs = []
    for verse in verses:
        if not verse.is_cross_verse:
            outputs.append(process_verse(verse))
    with open(Path(output_dir) / Path("nonpronominal_mention.tsv"), "w") as f:
        for s, c in outputs:
            f.write(f"{s}\t{c}\n")


@TaskSpec.register("nonpronominal_mentions")
class NonpronominalMentions(TaskSpec):
    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        process_verses(verses, output_dir)
