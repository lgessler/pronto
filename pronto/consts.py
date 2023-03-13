BOOKS_S2L = {
    "GEN": "Genesis",
    "EXO": "Exodus",
    "LEV": "Leviticus",
    "NUM": "Numbers",
    "DEU": "Deuteronomy",
    "JOS": "Joshua",
    "JDG": "Judges",
    "RUT": "Ruth",
    "1SA": "1 Samuel",
    "2SA": "2 Samuel",
    "1KI": "1 Kings",
    "2KI": "2 Kings",
    "1CH": "1 Chronicles",
    "2CH": "2 Chronicles",
    "EZR": "Ezra",
    "NEH": "Nehemiah",
    "TOB": "Tobias",
    "JDT": "Judith",
    "EST": "Esther",
    "JOB": "Job",
    "PSA": "Psalms",
    "PRO": "Proverbs",
    "ECC": "Ecclesiastes",
    "SNG": "Song of Solomon",
    "WIS": "Wisdom",
    "SIR": "Sirach",
    "ISA": "Isaiah",
    "JER": "Jeremiah",
    "LAM": "Lamentations",
    "BAR": "Baruch",
    "EZK": "Ezekiel",
    "DAN": "Daniel",
    "HOS": "Hosea",
    "JOL": "Joel",
    "AMO": "Amos",
    "OBA": "Obadiah",
    "JON": "Jonah",
    "MIC": "Micah",
    "NAM": "Nahum",
    "HAB": "Habakkuk",
    "ZEP": "Zephaniah",
    "HAG": "Haggai",
    "ZEC": "Zacharias",
    "MAL": "Malachi",
    "1MA": "1 Maccabees",
    "2MA": "2 Maccabees",
    "MAT": "Matthew",
    "MRK": "Mark",
    "LUK": "Luke",
    "JHN": "John",
    "ACT": "Acts",
    "ROM": "Romans",
    "1CO": "1 Corinthians",
    "2CO": "2 Corinthians",
    "GAL": "Galatians",
    "EPH": "Ephesians",
    "PHP": "Philippians",
    "COL": "Colossians",
    "1TH": "1 Thessalonians",
    "2TH": "2 Thessalonians",
    "1TI": "1 Timothy",
    "2TI": "2 Timothy",
    "TIT": "Titus",
    "PHM": "Philemon",
    "HEB": "Hebrews",
    "JAS": "James",
    "1PE": "1 Peter",
    "2PE": "2 Peter",
    "1JN": "1 John",
    "2JN": "2 John",
    "3JN": "3 John",
    "JUD": "Jude",
    "REV": "Revelation",
}
BOOKS_L2S = {v: k for k, v in BOOKS_S2L.items()}


ONTONOTES_BLACKLIST = {
    ("Matthew", 9, 6),  # 5-6
    ("Matthew", 9, 5),
    ("Matthew", 27, 66),  # Not included in OntoNotes
    ("Matthew", 27, 65),
    ("Matthew", 27, 64),
    ("Matthew", 27, 63),
    ("Matthew", 27, 58),
    ("Matthew", 27, 57),
    ("Matthew", 27, 59),
    ("Matthew", 27, 58),
    ("Matthew", 27, 60),
    ("Matthew", 27, 59),
    ("Matthew", 27, 61),
    ("Matthew", 27, 60),
    ("Matthew", 27, 62),
    ("Matthew", 27, 61),
    ("Matthew", 27, 63),
    ("Matthew", 27, 62),
    ("Ephesians", 1, 16),  # 15-16
    ("Ephesians", 1, 15),
    ("1 Thessalonians", 3, 2),  # 1-2
    ("1 Thessalonians", 3, 1),
    ("Mark", 5, 8),  # 7-8
    ("Mark", 5, 7),
    ("1 Corinthians", 5, 13),  # 12-13
    ("1 Corinthians", 5, 12),
    ("1 Corinthians", 6, 10),  # 9-10
    ("1 Corinthians", 6, 9),
    ("1 Corinthians", 12, 19),  # 18-19
    ("1 Corinthians", 12, 18),
    ("2 Corinthians", 12, 4),  # 3-4
    ("2 Corinthians", 12, 3),
    ("Romans", 1, 10),  # 9-10
    ("Romans", 1, 9),
    ("Romans", 1, 4),
    ("Romans", 1, 3),  # 3-4
    ("Romans", 3, 26),  # 25-26
    ("Romans", 3, 25),
    ("Romans", 8, 39),  # 38-39
    ("Romans", 8, 38),
    ("Romans", 9, 12),  # 11-12
    ("Romans", 9, 11),
    ("Hebrews", 6, 2),  # 1-2
    ("Hebrews", 6, 1),
    ("Hebrews", 6, 6),  # 4-6
    ("Hebrews", 6, 5),
    ("Hebrews", 6, 4),
    ("Hebrews", 7, 14),  # 13-14
    ("Hebrews", 7, 13),
    ("Hebrews", 11, 25),  # 24-25
    ("Hebrews", 11, 24),
    ("Hebrews", 11, 18),  # 17-18
    ("Hebrews", 11, 17),
    ("Hebrews", 13, 21),  # 20-21
    ("Hebrews", 13, 20),
    ("2 Thessalonians", 2, 17),  # 16-17
    ("2 Thessalonians", 2, 16),
    ("Galatians", 3, 27),  # 26-27
    ("Galatians", 3, 26),
    ("Galatians", 4, 11),  # 10-11
    ("Galatians", 4, 10),
    ("Acts", 1, 17),  # 16-17
    ("Acts", 1, 16),
    ("Acts", 1, 22),  # 21-22
    ("Acts", 1, 21),
    ("Acts", 1, 25),  # 24-25
    ("Acts", 1, 24),
    ("Acts", 3, 10),  # 9-10
    ("Acts", 3, 9),
    ("Acts", 4, 22),  # 21-22
    ("Acts", 4, 21),
    ("Acts", 5, 6),  # 5-6
    ("Acts", 5, 5),
    ("Acts", 8, 3),  # 1-3
    ("Acts", 8, 2),
    ("Acts", 8, 1),
    ("Acts", 11, 24),  # 23-24
    ("Acts", 11, 23),
    ("Acts", 13, 39),  # 38-39
    ("Acts", 13, 38),
    ("Acts", 19, 14),  # 13-14
    ("Acts", 19, 13),
    ("Acts", 20, 38),  # 37-38
    ("Acts", 20, 37),
    ("Acts", 21, 36),  # 35-36
    ("Acts", 21, 35),
    ("Acts", 24, 8),  # 6-8
    ("Acts", 24, 7),
    ("Acts", 24, 6),
    ("Acts", 24, 18),  # 17-18
    ("Acts", 24, 17),
    ("Acts", 24, 3),  # 2-3
    ("Acts", 24, 2),
    ("Acts", 28, 11),  # 10-11
    ("Acts", 28, 10),
    ("John", 1, 34),  # 32-34
    ("John", 1, 33),
    ("John", 1, 32),
    ("John", 10, 15),
    ("John", 10, 14),  # 14-15
    ("James", 1, 8),  # 7-8
    ("James", 1, 7),
    ("1 John", 3, 20),  # 19-20
    ("1 John", 3, 19),
    ("Luke", 1, 27),  # 26-27
    ("Luke", 1, 26),
    ("Luke", 4, 26),  # 25-26
    ("Luke", 4, 25),
    ("Luke", 5, 24),  # 23-24
    ("Luke", 5, 23),
    ("Luke", 5, 9),  # 8-9
    ("Luke", 5, 8),
    ("Luke", 8, 42),  # 41-42
    ("Luke", 8, 41),
    ("Luke", 8, 29),  # 28-29
    ("Luke", 8, 28),
    ("Luke", 11, 6),  # 5-6
    ("Luke", 11, 5),
    ("Luke", 22, 40),  # 39-40
    ("Luke", 22, 39),
    ("Luke", 23, 51),  # 50-51
    ("Luke", 23, 50),
    ("Luke", 24, 48),  # 47-48
    ("Luke", 24, 47),
    # ("Mark", 8, 38),  # Latin Clementine has 8:39??
    # ("John", 6, 72),  # Inconsistently split into just 71 or 71 and 72
    # ("John", 6, 71),
}
