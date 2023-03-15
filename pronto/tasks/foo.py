from typing import List

from pronto.aligning import AlignedVerse
from pronto.tasks.spec import TaskSpec


@TaskSpec.register("foo")
class Foo(TaskSpec):
    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        singles = 0
        cross = 0
        for verse in verses:
            if verse.is_one_to_one:
                singles += 1
            if verse.is_cross_verse:
                cross += 1

        print(singles, cross, len(verses), output_dir)
