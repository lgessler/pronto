import sys

import bs4
from bs4 import BeautifulSoup

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Provide input path and output path as arguments.")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        xml = BeautifulSoup(f.read(), features="lxml")

    for h in xml.find_all("h"):
        h.decompose()

    with open(sys.argv[2], "w") as f:
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
                    f.write("\t".join([book, chapter, verse, verse_buffer]) + "\n")
                verse = None
                verse_buffer = ""
            elif name is None and not isinstance(child, bs4.element.ProcessingInstruction):
                if book is not None and chapter is not None and verse is not None:
                    verse_buffer += " " + str(child).strip()
