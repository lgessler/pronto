from collections import defaultdict
from dataclasses import dataclass
from typing import List

from pronto.consts import BOOKS_L2S, BOOKS_S2L


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
    books = defaultdict(lambda: defaultdict(lambda: dict()))
    book = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip().split("\t")
            book_id = line[0]
            chapter_id = int(line[1])
            if book_id not in book:
                book.append(book_id)
            verse_id = int(line[2])
            body = line[3]
            books[book_id][chapter_id][verse_id] = body

    for book_id in books:
        if book_id not in BOOKS_S2L:
            raise ValueError(f"Unknown bookcode: {book_id}")

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
