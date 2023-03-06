from typing import List, Tuple

from onf_parser import Section, parse_files
from tango import DillFormat, Step

from pronto.aligning import align_verses
from pronto.reading import Book, read_bible_tsv


@Step.register("pronto.steps::read_ontonotes")
class ReadOntonotes(Step):
    DETERMINISTIC = True
    CACHEABLE = True
    FORMAT = DillFormat()

    def run(self, path: str) -> List[Tuple[str, List[Section]]]:
        return parse_files(path)


@Step.register("pronto.steps::read_bible_tsv")
class ReadBibleTsv(Step):
    DETERMINISTIC = True
    CACHEABLE = True
    FORMAT = DillFormat()

    def run(self, path: str) -> List[Book]:
        return read_bible_tsv(path)


@Step.register("pronto.steps::align_verses")
class AlignVerses(Step):
    DETERMINISTIC = True
    CACHEABLE = True
    FORMAT = DillFormat()

    def run(self, ontonotes_data: List[Tuple[str, List[Section]]], bible_data: List[Book]):
        return align_verses(ontonotes_data, bible_data)
