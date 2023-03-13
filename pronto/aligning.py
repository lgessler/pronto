from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple, Dict
import logging

from onf_parser import Section
from onf_parser.models import Sentence, SpeakerInformation

from pronto.consts import BOOKS_S2L
from pronto.reading import Book, Verse


logger = logging.getLogger(__name__)


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


def _index_ontonotes(
    ontonotes_data: List[Tuple[str, List[Section]]]
) -> Dict[str, Dict[str, Dict[str, List[Sentence]]]]:
    index = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for filename, sections in ontonotes_data:
        for section in sections:
            for sentence in section.sentences:
                if sentence.speaker_information is None:
                    continue
                book, start, stop = _parse_ontonotes_speaker_info(sentence.speaker_information)
                book = book.replace("_", " ")
                for chapter, verse, _ in start + stop:
                    if sentence not in index[book][chapter][verse]:
                        index[book][chapter][verse].append(sentence)

    return index


def _index_bible_data(bible_data: List[Book]) -> Dict[str, Dict[str, Dict[str, List[Sentence]]]]:
    index = defaultdict(lambda: defaultdict(dict))
    for book in bible_data:
        book_id = BOOKS_S2L[book.id]
        for chapter in book.chapters:
            for verse in chapter.verses:
                index[book_id][chapter.id][verse.id] = verse
    return index


@dataclass
class AlignedVerse:
    verse: Verse
    ontonotes_sentences: List[Tuple[str, Sentence]]


def align_verses(ontonotes_data: List[Tuple[str, List[Section]]], bible_data: List[Book]):
    ontonotes_verse_index = _index_ontonotes(ontonotes_data)
    bible_verse_index = _index_bible_data(bible_data)

    bible_books = set(bible_verse_index.keys())
    ontonotes_books = set(ontonotes_verse_index.keys())
    common_books = bible_books.intersection(ontonotes_books)
    only_ontonotes_books = ontonotes_books.difference(bible_books)

    if len(only_ontonotes_books) > 0:
        logger.warning(f"The following books were not found in the Bible translation:"
                       f" {only_ontonotes_books}.\n\nDoes this look right? Consider editing consts.py.")

    print(common_books)


    assert False
