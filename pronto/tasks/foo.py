from typing import List

from pronto.aligning import AlignedVerse
from pronto.tasks.spec import TaskSpec


@TaskSpec.register("foo")
class Foo(TaskSpec):
    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        ...
