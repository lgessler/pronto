from os import makedirs
from shutil import rmtree
from typing import List, Tuple

from onf_parser import Section, parse_files
from tango import DillFormat, Step

from pronto.aligning import AlignedVerse, align_verses
from pronto.reading import Book, read_bible_tsv
from pronto.tasks.spec import TaskSpec


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

    def run(
        self, ontonotes_data: List[Tuple[str, List[Section]]], bible_data: List[Book], threshold: int = 500
    ) -> List[AlignedVerse]:
        return align_verses(ontonotes_data, bible_data, threshold)


@Step.register("pronto.steps::generate_task_data")
class GenerateTaskData(Step):
    DETERMINISTIC = True
    CACHEABLE = True

    def run(self, task_specs: List[TaskSpec], verses: List[AlignedVerse], output_dir: str):
        rmtree(output_dir, ignore_errors=True)
        makedirs(output_dir)
        for s in task_specs:
            s.process(verses, output_dir)
