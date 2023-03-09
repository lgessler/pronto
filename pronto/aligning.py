from typing import List, Tuple

from onf_parser import Section
from onf_parser.models import SpeakerInformation

from pronto.reading import Book

def _parse_ontonotes_time(s: str):
    pieces = s.split(":")
    pieces = [p.split("_") for p in pieces]
    assert all(len(p) == 3 for p in pieces)
    return pieces

def _parse_ontonotes_speaker_info(info: SpeakerInformation):
    book = info.name
    start = _parse_ontonotes_time(info.start_time)
    stop = _parse_ontonotes_time(info.stop_time)
    return book, start, stop

def _index_ontonotes(ontonotes_data):
    for filename, sections in ontonotes_data:
        for section in sections:
            for sentence in section.sentences:
                if sentence.speaker_information is None:
                    continue
                book, start, stop = _parse_ontonotes_speaker_info(sentence.speaker_information)
                print(book, start, stop)



def align_verses(ontonotes_data: List[Tuple[str, List[Section]]], bible_data: List[Book]):
    ontonotes_verse_index = _index_ontonotes(ontonotes_data)
    bible_verse_index = {}







    assert False
