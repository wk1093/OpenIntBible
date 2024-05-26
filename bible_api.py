import csv
import io
from xml.etree import ElementTree as xml
import inspect
# OpenGNT_version3_3.csv is a csv file containing the Greek New Testament
# with Strong's numbers and morphology
# Format:
# OGNTsort	TANTTsort	FEATURESsort1	LevinsohnClauseID	OTquotation	〔BGBsortI｜LTsortI｜STsortI〕	〔Book｜Chapter｜Verse〕	〔OGNTk｜OGNTu｜OGNTa｜lexeme｜rmac｜sn〕	〔BDAGentry｜EDNTentry｜MounceEntry｜GoodrickKohlenbergerNumbers｜LN-LouwNidaNumbers〕

# OpenGNT_TranslationByClause.csv is a csv file containing the Greek New Testament translated into English
# Format:
# LevinsohnClauseID	IT	LT	ST

from fcache import cache


csv_file = 'OpenGNT_version3_3.csv'

def get_greek_data():
    with open(csv_file, 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            reader = csv.reader(text_file, delimiter='\t')
            for row in reader:
                yield row

def get_eng_data():
    with open('OpenGNT_TranslationByClause.csv', 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            reader = csv.reader(text_file, delimiter='\t')
            for row in reader:
                yield row

@cache
def greek_data():
    return list(get_greek_data())

@cache
def eng_data():
    return list(get_eng_data())


def isf(x):
    return inspect.isroutine(x) or inspect.isclass(x)

class GreekWord:
    def __init__(self, csvdata):
        # csvdata:
        # ['OGNTsort', 'TANTTsort', 'FEATURESsort1', 'LevinsohnClauseID', 'OTquotation', '〔BGBsortI｜LTsortI｜STsortI〕',
        # '〔Book｜Chapter｜Verse〕', '〔OGNTk｜OGNTu｜OGNTa｜lexeme｜rmac｜sn〕',
        # '〔BDAGentry｜EDNTentry｜MounceEntry｜GoodrickKohlenbergerNumbers｜LN-LouwNidaNumbers〕',
        # '〔transSBLcap｜transSBL｜modernGreek｜Fonética_Transliteración〕', '〔TBESG｜IT｜LT｜ST｜Español〕',
        # '〔PMpWord｜PMfWord〕', '〔Note｜Mvar｜Mlexeme｜Mrmac｜Msn｜MTBESG〕']
        self.OGNTsort = csvdata[0]
        self.TANTTsort = csvdata[1]
        self.FEATURESsort1 = csvdata[2]
        self.LevinsohnClauseID = csvdata[3]
        self.OTquotation = csvdata[4]
        self.BGBsortI, self.LTsortI, self.STsortI = csvdata[5][1:-1].split('｜')
        try:
            self.Book, self.Chapter, self.Verse = map(int, csvdata[6][1:-1].split('｜'))
        except ValueError:
            self.Book, self.Chapter, self.Verse = 0, 0, 0
        self.OGNTk, self.OGNTu, self.OGNTa, self.lexeme, self.rmac, self.sn = csvdata[7][1:-1].split('｜')
        self.BDAGentry, self.EDNTentry, self.MounceEntry, self.GoodrickKohlenbergerNumbers, self.LN_LouwNidaNumbers = csvdata[8][1:-1].split('｜')
        self.transSBLcap, self.transSBL, self.modernGreek, self.Fonetica_Transliteracion = csvdata[9][1:-1].split('｜')
        self.TBESG, self.IT, self.LT, self.ST, self.Espanol = csvdata[10][1:-1].split('｜')
        self.PMpWord, self.PMfWord = csvdata[11][1:-1].split('｜')
        self.Note, self.Mvar, self.Mlexeme, self.Mrmac, self.Msn, self.MTBESG = csvdata[12][1:-1].split('｜')

    def __str__(self):
        return "GreekWord(" + ', '.join(f'{attr}={getattr(self, attr)}' for attr in dir(self) if not attr.startswith('__') and not isf(getattr(self, attr))) + ")"

    def __repr__(self):
        return "GreekWord(" + ', '.join(f'{attr}={getattr(self, attr)}' for attr in dir(self) if not attr.startswith('__') and not isf(getattr(self, attr))) + ")"


class GreekVerse:
    def __init__(self, words):
        self.words: list[GreekWord] = words
        # make sure all the words are in the same verse, chapter, and book
        for word in words:
            if word.Book != words[0].Book or word.Chapter != words[0].Chapter or word.Verse != words[0].Verse:
                raise ValueError("All words must be in the same verse")
        self.book = words[0].Book
        self.chapter = words[0].Chapter
        self.verse_num = words[0].Verse

    def __str__(self):
        return "GreekVerse(" + ', '.join(f'{attr}={getattr(self, attr)}' for attr in dir(self) if not attr.startswith('__') and not isf(getattr(self, attr))) + ")"

    def __repr__(self):
        return "GreekVerse(" + ', '.join(f'{attr}={getattr(self, attr)}' for attr in dir(self) if not attr.startswith('__') and not isf(getattr(self, attr))) + ")"

    def sort_st(self):
        self.words.sort(key=lambda x: x.STsortI)

    def sort_lt(self):
        self.words.sort(key=lambda x: x.LTsortI)

    def ST(self):
        # for each word in the verse, get the LevinsionClauseID
        ids = set()
        for word in self.words:
            ids.add(word.LevinsohnClauseID.strip().lower())
        # get the English translation of the verse
        final = ""
        for row in eng_data():
            if row[0].strip().lower() in ids:
                final += row[3] + ' '
        return final

    def LT(self):
        # for each word in the verse, get the LevinsionClauseID
        ids = set()
        for word in self.words:
            ids.add(word.LevinsohnClauseID.strip().lower())
        # get the English translation of the verse
        final = ""
        for row in eng_data():
            if row[0].strip().lower() in ids:
                final += row[2] + ' '
        return final

    def IT(self):
        # for each word in the verse, get the LevinsionClauseID
        ids = set()
        for word in self.words:
            ids.add(word.LevinsohnClauseID.strip().lower())
        # get the English translation of the verse
        final = ""
        for row in eng_data():
            if row[0].strip().lower() in ids:
                final += row[1] + ' '
        return final

# used to select a few verses
class GreekSection:
    def __init__(self, verses):
        self.verses: list[GreekVerse] = verses
        # make sure all the verses are in the same chapter and book
        for verse in verses:
            if verse.book != verses[0].book or verse.chapter != verses[0].chapter:
                raise ValueError("All verses must be in the same chapter")
        self.book = verses[0].book
        self.chapter = verses[0].chapter

    def __str__(self):
        return "GreekSection(" + ', '.join(f'{attr}={getattr(self, attr)}' for attr in dir(self) if not attr.startswith('__') and not isf(getattr(self, attr))) + ")"

    def __repr__(self):
        return "GreekSection(" + ', '.join(f'{attr}={getattr(self, attr)}' for attr in dir(self) if not attr.startswith('__') and not isf(getattr(self, attr))) + ")"

    def ST(self):
        final = ""
        for verse in self.verses:
            final += verse.ST()
        return final

    def LT(self):
        final = ""
        for verse in self.verses:
            final += verse.LT()
        return final

    def IT(self):
        final = ""
        for verse in self.verses:
            final += verse.IT()
        return final

    def words(self):
        return [word for verse in self.verses for word in verse.words]





class GreekChapter:
    def __init__(self, verses):
        self.verses: list[GreekVerse] = verses
        # make sure all the verses are in the same chapter and book
        for verse in verses:
            if verse.book != verses[0].book or verse.chapter != verses[0].chapter:
                raise ValueError("All verses must be in the same chapter")
        self.book = verses[0].book
        self.chapter = verses[0].chapter

    def __str__(self):
        return "GreekChapter(" + ', '.join(f'{attr}={getattr(self, attr)}' for attr in dir(self) if not attr.startswith('__') and not isf(getattr(self, attr))) + ")"

    def __repr__(self):
        return "GreekChapter(" + ', '.join(f'{attr}={getattr(self, attr)}' for attr in dir(self) if not attr.startswith('__') and not isf(getattr(self, attr))) + ")"

    def range(self, start: int, end: int):
        return GreekSection(self.verses[start:end])


@cache
def get_greek_chapter(book: int, chapter: int) -> GreekChapter:
    print("loading greek chapter")
    words = []
    for row in greek_data():
        word = GreekWord(row)
        if word.Book == book and word.Chapter == chapter:
            words.append(word)
    # group the words into verses
    verses = []
    cur_verse = []
    if not words:
        raise ValueError(f"Chapter {chapter} not found in book {book}")
    verse_num = words[0].Verse
    for word in words:
        if word.Verse != verse_num:
            verses.append(GreekVerse(cur_verse))
            cur_verse = []
            verse_num = word.Verse
        cur_verse.append(word)
    if cur_verse:
        verses.append(GreekVerse(cur_verse))
    return GreekChapter(verses)

class StrongsDefinition:
    def __init__(self, number):
        # use strongsgreek.xml to get the definition of the strongs number
        if isinstance(number, int):
            num = number
        elif isinstance(number, str):
            if number[0] == 'G':
                num = int(number[1:])
            else:
                num = int(number)
        else:
            raise ValueError("Invalid input")
        with open('strongsgreek.xml', 'rb') as f:
            with io.TextIOWrapper(f, encoding='utf-8') as text_file:
                data = text_file.read()
        try:
            root = xml.fromstring(data)
        except xml.ParseError:
            raise ValueError("Invalid XML")
        for entry in root.findall('.//entry'):
            a: xml.Element = entry
            if int(entry.attrib['strongs']) == num:
                self.strongs = num
                self.greek = entry.find('greek').attrib['unicode']
                self.translit = entry.find('greek').attrib['translit']
                self.pronunciation = entry.find('pronunciation').attrib['strongs']
                try:
                    self.strongs_derivation = entry.find('strongs_derivation').text
                except AttributeError:
                    self.strongs_derivation = None
                try:
                    self.strongs_def = entry.find('strongs_def').text
                except AttributeError:
                    self.strongs_def = None
                try:
                    self.kjv_def = entry.find('kjv_def').text
                except AttributeError:
                    self.kjv_def = None
                self.text = entry
                self.see = []
                for see in entry.findall('.//see'):
                    self.see.append(see.attrib)
                return
        raise ValueError(f"Strong's number not found: '{number}'")

    def __str__(self):
        return f'{self.strongs} {self.greek} {self.pronunciation}'


def is_new_testament(book):
    if isinstance(book, int):
        return 39 < book < 67
    elif isinstance(book, str):
        if book.isdigit():
            return 39 < int(book) < 67
        else:
            return book.capitalize().strip() in ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation']
    return False

def get_book_names():
    return ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation']

def get_book_sizes():
    return [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]

@cache
def to_html(verses):
    print("building html...")
    # for verse in gch.verses:
    #     if verse.verse_num != int(selected_verse):
    #         main += f"""<span class="verse" id="verse{verse.verse_num}"><b>{verse.verse_num}</b> {verse.ST()}</span>"""
    #     else:
    #         main += f"""<span class="verse selected" id="verse{verse.verse_num}"><b>{verse.verse_num}</b> {verse.ST()}</span>"""
    # that is the old code, but it is too slow
    # this new code is faster
    main = ""
    for verse in verses.verses:
        main += f"""<span class="verse" id="verse{verse.verse_num}"><b>{verse.verse_num}</b> {verse.ST()}</span>"""
    return main