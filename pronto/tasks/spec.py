from typing import List

from tango.common import Registrable

from pronto.aligning import AlignedVerse


class TaskSpec(Registrable):
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def process(self, verses: List[AlignedVerse]) -> None:
        raise NotImplemented()
