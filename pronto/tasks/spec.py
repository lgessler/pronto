from typing import List

from tango.common import Registrable

from pronto.aligning import AlignedVerse


class TaskSpec(Registrable):
    def process(self, verses: List[AlignedVerse], output_dir: str) -> None:
        raise NotImplemented()
