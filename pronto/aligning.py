from typing import List, Tuple

from onf_parser import Section

from pronto.reading import Book


def align_verses(ontonotes_data: List[Tuple[str, List[Section]]], bible_data: List[Book]):
    print(ontonotes_data)
