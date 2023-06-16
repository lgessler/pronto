import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from onf_parser import Section
from onf_parser.models import Coref, Sentence, SpeakerInformation

from pronto.consts import BOOKS_S2L, ONTONOTES_BLACKLIST
from pronto.reading import Book, Verse

logger = logging.getLogger(__name__)


@dataclass
class AlignedVerse:
    book: str
    chapter: int
    verse_id: int
    verse: Verse
    ontonotes_sentences: List[Sentence]

    @property
    def is_one_to_one(self) -> bool:
        """
        True iff there is exactly one corresponding OntoNotes sentence
        """
        return len(self.ontonotes_sentences) == 1

    @property
    def is_cross_verse(self) -> bool:
        """
        True iff any OntoNotes sentence crosses over into neighboring verses
        """
        if hasattr(self, "__is_cross_verse"):
            return self.__is_cross_verse
        else:
            for sentence in self.ontonotes_sentences:
                _, start, stop = _parse_ontonotes_speaker_info(sentence.speaker_information)
                for _, verse, _ in start + stop:
                    verse = int(verse)
                    if verse != self.verse_id:
                        self.__is_cross_verse = True
                        return True
            self.__is_cross_verse = False
            return False

    @property
    def mentions(self) -> List[Coref]:
        mentions = []
        for sentence in self.ontonotes_sentences:
            for leaf in sentence.leaves:
                if leaf.coref is not None:
                    mentions.append(leaf.coref)
        return mentions

    @property
    def reference(self):
        return f"{self.book} {self.chapter}:{self.verse_id}"


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
                    chapter = int(chapter)
                    verse = int(verse)
                    if (
                        verse not in index[book][chapter].keys() or sentence not in index[book][chapter][verse]
                    ) and not (book, chapter, verse) in ONTONOTES_BLACKLIST:
                        index[book][chapter][verse].append(sentence)

    return index


def _index_bible_data(bible_data: List[Book]) -> Dict[str, Dict[str, Dict[str, Verse]]]:
    index = defaultdict(lambda: defaultdict(dict))
    for book in bible_data:
        book_id = BOOKS_S2L[book.id] if book.id in BOOKS_S2L else book.id
        for chapter in book.chapters:
            for verse in chapter.verses:
                if (book_id, chapter.id, verse.id) not in ONTONOTES_BLACKLIST:
                    index[book_id][chapter.id][verse.id] = verse
    return index


def align_verses(
    ontonotes_data: List[Tuple[str, List[Section]]], bible_data: List[Book], threshold: int
) -> List[AlignedVerse]:
    ontonotes_verse_index = _index_ontonotes(ontonotes_data)
    bible_verse_index = _index_bible_data(bible_data)

    bible_books = set(bible_verse_index.keys())
    ontonotes_books = set(ontonotes_verse_index.keys())
    common_books = bible_books.intersection(ontonotes_books)
    only_ontonotes_books = ontonotes_books.difference(bible_books)

    if len(only_ontonotes_books) > 0:
        logger.warning(
            f"The following books were not found in the Bible translation:"
            f" {only_ontonotes_books}.\n\nDoes this look right? Consider editing consts.py."
        )

    aligned = []
    misses = []
    for book in common_books:
        bible_chapters = bible_verse_index[book].keys()
        ontonotes_chapters = ontonotes_verse_index[book].keys()
        if bible_chapters != ontonotes_chapters:
            logger.warning(f"Chapters do not match for {book}! Bible: {bible_chapters}; Onto: {ontonotes_chapters}")
        for chapter in ontonotes_chapters:
            bible_verses = bible_verse_index[book][chapter].keys()
            ontonotes_verses = ontonotes_verse_index[book][chapter].keys()
            if bible_verses != ontonotes_verses:
                onto_diff = set(bible_verses).difference(set(ontonotes_verses))
                bible_diff = set(ontonotes_verses).difference(set(bible_verses))
                logger.warning(
                    f"Verses do not match for {book} {chapter}!"
                    + (f" Missing in OntoNotes: {onto_diff}" if len(onto_diff) > 0 else "")
                    + (f" Missing in Bible: {bible_diff}" if len(bible_diff) > 0 else "")
                )
            for verse_id, verses in ontonotes_verse_index[book][chapter].items():
                if (
                    book in bible_verse_index
                    and chapter in bible_verse_index[book]
                    and verse_id in bible_verse_index[book][chapter]
                ):
                    aligned.append(
                        AlignedVerse(book, chapter, verse_id, bible_verse_index[book][chapter][verse_id], verses)
                    )
                else:
                    misses.append((chapter, book, verse_id))

    logger.info(f"Aligned {len(aligned)} verses; failed to align {len(misses)} from OntoNotes verses")
    if len(aligned) < threshold:
        raise ValueError(f"Aborting run due to insufficient aligned verse count: {len(aligned)}")
    return aligned
