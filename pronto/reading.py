from collections import defaultdict
from dataclasses import dataclass
from logging import getLogger
from typing import List

from pronto.consts import BOOKS_L2S, BOOKS_S2L

logger = getLogger(__name__)


@dataclass
class Verse:
    id: int
    body: str


@dataclass
class Chapter:
    id: int
    verses: List[Verse]

    @property
    def indexed_verses(self):
        return {v.id: v for v in self.verses}


@dataclass
class Book:
    id: str
    chapters: List[Chapter]

    @property
    def indexed_chapters(self):
        return {c.id: c for c in self.chapters}


def read_bible_tsv(path: str) -> List[Book]:
    logger.info(f"Reading from {path}")
    books = defaultdict(lambda: defaultdict(lambda: dict()))
    book = []
    with open(path, "r") as f:
        for line in f:
            try:
                pieces = line.split("\t")
                book_id = pieces[0]
                chapter_id = int(pieces[1])
                if book_id not in book:
                    book.append(book_id)
                try:
                    verse_id = int(pieces[2])
                except ValueError:
                    logger.warning(f"{book_id} {chapter_id}: found non-integer verse {pieces[2]}. Skipping.")
                    continue
                body = pieces[3]
                if body.strip() == "":
                    logger.warning(f"{book_id} {chapter_id}: verse {pieces[2]} is empty. Skipping.")
                    continue
                books[book_id][chapter_id][verse_id] = body.strip()
            except Exception as e:
                logger.error(f"Error encountered while handling a line: {line} ({pieces})")
                logger.exception(e)

    for book_id in books:
        if book_id not in BOOKS_S2L:
            logger.warning(f"Unknown bookcode: {book_id}")

    book_objs = []
    for book_id in BOOKS_S2L.keys():
        if book_id in books:
            chapter_objs = []
            for chapter_id, verses in sorted(books[book_id].items(), key=lambda x: x[0]):
                verse_objs = []
                for verse_id, verse in sorted(verses.items(), key=lambda x: x[0]):
                    verse_objs.append(Verse(verse_id, verse))
                chapter_objs.append(Chapter(chapter_id, verse_objs))
            book_objs.append(Book(book_id, chapter_objs))
    return book_objs
