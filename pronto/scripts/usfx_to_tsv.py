import csv
import sys

import bs4
from bs4 import BeautifulSoup

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Provide input path and output path as arguments.")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        xml = BeautifulSoup(f.read(), features="lxml")

    def remove_all_tags(tag_name):
        for x in xml.find_all(tag_name):
            x.decompose()

    # see https://ebible.org/usfx/usfx.htm
    remove_all_tags("h")  # header
    remove_all_tags("f")  # footnote
    remove_all_tags("cl")  # chapter label
    remove_all_tags("generated")  # generated content
    remove_all_tags("ref")  # reference

    with open(sys.argv[2], "w", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        book = None
        chapter = None
        verse = None
        verse_buffer = ""
        for child in xml.recursiveChildGenerator():
            name = child.name
            if name == "book":
                book = child.attrs["id"]
            elif name == "c":
                chapter = child.attrs["id"]
            elif name == "v":
                verse = child.attrs["id"]
            elif name == "ve":
                if book is not None and chapter is not None and verse is not None:
                    verse_buffer = verse_buffer.replace("\n", " ")
                    verse_buffer = verse_buffer.replace("\t", " ")
                    verse_buffer = verse_buffer.strip()
                    writer.writerow([book, chapter, verse, verse_buffer])
                verse = None
                verse_buffer = ""
            elif name is None and not isinstance(child, bs4.element.ProcessingInstruction):
                if book is not None and chapter is not None and verse is not None:
                    verse_buffer += " " + str(child).strip()
