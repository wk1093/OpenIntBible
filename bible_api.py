import csv
import io
import json
import os
import time
import zipfile
from dataclasses import dataclass

from fcache import cache, mem_cache

# Greek:
# OpenGNT_TranslationByClause.csv
# OpenGNT_version3_3.csv
# strongs-greek-dictionary.js
# strongsgreek.dat

# Hebrew:
# BHSA-with-extended-features.csv
# BHSA-clause-translation.csv
# strongs-hebrew-dictionary.js

if os.path.exists('data') and not os.path.exists('data.zip'):
    print("zipping data...")
    zipf = zipfile.ZipFile('data.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk('data'):
        for file in files:
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join('data', '..')))
    zipf.close()
    print("data.zip created")

if not os.path.exists('data'):
    print("unzipping data...")
    # unzip data.zip
    with zipfile.ZipFile('data.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
    print("data unzipped")

print("preloading...")
preloadtime = time.time()


def get_greek_data():
    with open('data/OpenGNT_version3_3.csv', 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            reader = csv.reader(text_file, delimiter='\t')
            for row in reader:
                yield row


def get_greek_clause_data():
    with open('data/OpenGNT_TranslationByClause.csv', 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            reader = csv.reader(text_file, delimiter='\t')
            for row in reader:
                yield row


@cache
def get_greek_strongs_data() -> dict:
    with open('data/strongs-greek-dictionary.js', 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            data = text_file.read()
            a_t = "var strongsGreekDictionary = "
            a = data.find(a_t)
            b = data.find("; module.exports = strongsGreekDictionary;")
            data = data[a + len(a_t):b]
            data = json.loads(data)

    return data


def get_hebrew_data():
    with open('data/BHSA-with-extended-features.csv', 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            reader = csv.reader(text_file, delimiter='\t')
            for row in reader:
                yield row


def get_hebrew_clause_data():
    with open('data/BHSA-clause-translation.csv', 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            reader = csv.reader(text_file, delimiter='\t')
            for row in reader:
                yield row


@cache
def get_hebrew_strongs_data():
    with open('data/strongs-hebrew-dictionary.js', 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            data = text_file.read()
            a_t = "var strongsHebrewDictionary = "
            a = data.find(a_t)
            b = data.find(";\n\nmodule.exports = strongsHebrewDictionary;")
            data = data[a + len(a_t):b]
            data = json.loads(data)
    return data


def greek_data():
    return list(get_greek_data())


greek_dat = greek_data()


def greek_clause_data():
    data = {}
    for row in get_greek_clause_data():
        data[row[0].strip().lower()] = row
    return data


greek_clause_dat = greek_clause_data()


@cache
def greek_strongs_data():
    # use strongsgreek.dat to get the pronunciation and other details not in the json file
    dat = get_greek_strongs_data()
    with open('data/strongsgreek.dat', 'rb') as f:
        with io.TextIOWrapper(f, encoding='utf-8') as text_file:
            data = text_file.read()
            for key, value in dat.items():
                # number format is $$T0000001
                k = int(key[1:])
                a_t = f"$$T{k:07}"
                a = data.find(a_t)
                # next line should start with a \
                b = data.find('\n', a)
                if data[b + 1] != '\\':
                    print("incorrect")

                # next line should contain the following data:
                # {NUM}  {TRANSLIT}  {PRONUNCIATION}
                # where everything inside the {} is the actual data (there is no {} in the file)
                c = data.find('\n ', b + 1)  # beginning of the line
                d = data.find('\n', c + 1)  # end of the line
                e = data.rfind('  ', c, d)  # start of pronunciation
                pron = data[e + 2:d].strip()

                dat[key]['pronunciation'] = pron
    return dat


greek_strongs_dat = greek_strongs_data()


def hebrew_data():
    return list(get_hebrew_data())[1:]


hebrew_dat = hebrew_data()


def hebrew_clause_data():
    data = {}
    for row in get_hebrew_clause_data():
        data[row[0].strip().lower()] = row
    return data


hebrew_clause_dat = hebrew_clause_data()


@cache
def hebrew_strongs_data():
    return get_hebrew_strongs_data()


hebrew_strongs_dat = hebrew_strongs_data()

donepreload = time.time()
print("done!")
print(f"preload time: {donepreload - preloadtime}")


@dataclass(init=False)
class GreekWord:
    OGNTsort: str
    TANTTsort: str
    FEATURESsort1: str
    LevinsohnClauseID: str
    OTquotation: str
    BGBsortI: str
    LTsortI: str
    STsortI: str
    Book: int
    Chapter: int
    Verse: int
    OGNTk: str
    OGNTu: str
    OGNTa: str
    lexeme: str
    rmac: str
    sn: str
    BDAGentry: str
    EDNTentry: str
    MounceEntry: str
    GoodrickKohlenbergerNumbers: str
    LN_LouwNidaNumbers: str
    transSBLcap: str
    transSBL: str
    modernGreek: str
    Fonetica_Transliteracion: str
    TBESG: str
    IT: str
    LT: str
    ST: str
    Espanol: str
    PMpWord: str
    PMfWord: str
    Note: str
    Mvar: str
    Mlexeme: str
    Mrmac: str
    Msn: str
    MTBESG: str

    def __init__(self, csvdata):
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
        self.BDAGentry, self.EDNTentry, self.MounceEntry, self.GoodrickKohlenbergerNumbers, self.LN_LouwNidaNumbers = \
            csvdata[8][1:-1].split('｜')
        self.transSBLcap, self.transSBL, self.modernGreek, self.Fonetica_Transliteracion = csvdata[9][1:-1].split('｜')
        self.TBESG, self.IT, self.LT, self.ST, self.Espanol = csvdata[10][1:-1].split('｜')
        self.PMpWord, self.PMfWord = csvdata[11][1:-1].split('｜')
        self.Note, self.Mvar, self.Mlexeme, self.Mrmac, self.Msn, self.MTBESG = csvdata[12][1:-1].split('｜')

        self.DEF = self.TBESG

        self.badStrongs = self.sn not in greek_strongs_dat.keys()

    def __hash__(self):
        return hash(self.__repr__())


@dataclass(init=False)
class HebrewWord:
    BHSwordSort: int
    paragraphMarker: str
    poetryMarker: str
    KJVverseSort: int
    KJVbook: int
    KJVchapter: int
    KJVverse: int
    BHSverseSort: int
    BHSbook: int
    BHSchapter: int
    BHSverse: int
    clauseID: str
    clauseKind: str
    clauseType: str
    language: str
    BHSwordPointed: str
    BHSwordConsonantal: str
    SBLstyleTransliteration: str
    poneticTranscription: str
    HebrewLexeme: str
    lexemeID: str
    sn: str
    extendedStrongNumber: str
    morphologyCode: str
    morphologyDetail: str
    ETCBCgloss: str
    extendedGloss: str
    BSBsort: float
    BSB: str

    def __init__(self, csvdata, lastSort=99999.0):
        self.BHSwordSort = int(csvdata[0])
        self.paragraphMarker = csvdata[1]
        self.poetryMarker = csvdata[2]
        self.KJVverseSort, self.KJVbook, self.KJVchapter, self.KJVverse = map(int, csvdata[3][1:-1].split('｜'))
        self.BHSverseSort, self.BHSbook, self.BHSchapter, self.BHSverse = map(int, csvdata[4][1:-1].split('｜'))
        self.clauseID = csvdata[5]
        self.clauseKind = csvdata[6]
        self.clauseType = csvdata[7]
        self.language = csvdata[8]
        if self.language != 'Hebrew':
            raise ValueError("Not a Hebrew word, language = " + self.language)
        self.BHSwordPointed = csvdata[9]
        self.BHSwordConsonantal = csvdata[10]
        self.SBLstyleTransliteration = csvdata[11]
        self.poneticTranscription = csvdata[12]
        self.HebrewLexeme = csvdata[13]
        self.lexemeID = csvdata[14]
        self.sn = csvdata[15]
        self.extendedStrongNumber = csvdata[16]
        if len(self.sn) == 0:
            self.sn = self.extendedStrongNumber
        self.morphologyCode = csvdata[17]
        self.morphologyDetail = csvdata[18]
        self.ETCBCgloss = csvdata[19]
        self.extendedGloss = csvdata[20]
        if '＠' not in csvdata[21]:
            self.BSBsort = lastSort
            self.BSB = '-'
        else:
            self.BSBsort, self.BSB = csvdata[21][1:-1].split('＠')
            self.BSBsort = int(self.BSBsort)

        self.transSBLcap = self.SBLstyleTransliteration
        self.lexeme = self.HebrewLexeme[5:-6]
        self.TBESG = self.ETCBCgloss
        self.ST = self.BSB

        self.badStrongs = self.sn not in hebrew_strongs_dat.keys()

        self.DEF = self.extendedGloss

    def __hash__(self):
        return hash(self.__repr__())


@dataclass(init=False)
class GreekVerse:
    words: list[GreekWord]
    book: int
    chapter: int
    verse_num: int

    def __init__(self, words):
        self.words: list[GreekWord] = words
        # make sure all the words are in the same verse, chapter, and book
        for word in words:
            if word.Book != words[0].Book or word.Chapter != words[0].Chapter or word.Verse != words[0].Verse:
                raise ValueError("All words must be in the same verse")
        self.book = words[0].Book
        self.chapter = words[0].Chapter
        self.verse_num = words[0].Verse

    def sort_st(self):
        self.words.sort(key=lambda x: x.STsortI)

    def sort_lt(self):
        self.words.sort(key=lambda x: x.LTsortI)

    def ST(self):
        ids = list()
        copy = GreekVerse(self.words)
        copy.sort_st()
        for word in copy.words:
            ids.append(word.LevinsohnClauseID.strip().lower())
        ids = list(dict.fromkeys(ids))
        final = ""
        for id_ in ids:
            row = greek_clause_dat.get(id_, None)
            if row:
                final += row[3] + ' '
        return final

    def LT(self):
        # for each word in the verse, get the LevinsionClauseID
        ids = list()
        copy = GreekVerse(self.words)
        copy.sort_lt()
        for word in copy.words:
            ids.append(word.LevinsohnClauseID.strip().lower())
        # get the English translation of the verse
        final = ""
        for id_ in ids:
            row = greek_clause_dat.get(id_, None)
            if row:
                final += row[2] + ' '
        return final

    def IT(self):
        # for each word in the verse, get the LevinsionClauseID
        ids = list()
        copy = GreekVerse(self.words)
        copy.sort_lt()
        for word in copy.words:
            ids.append(word.LevinsohnClauseID.strip().lower())
        # get the English translation of the verse
        final = ""
        for id_ in ids:
            row = greek_clause_dat.get(id_, None)
            if row:
                final += row[1] + ' '
        return final

    def __hash__(self):
        return hash(self.__repr__())


@dataclass(init=False)
class HebrewVerse:
    words: list[HebrewWord]
    book: int
    chapter: int
    verse_num: int

    def __init__(self, words):
        self.words: list[HebrewWord] = words
        # make sure all the words are in the same verse, chapter, and book
        for word in words:
            if word.BHSbook != words[0].BHSbook or word.BHSchapter != words[0].BHSchapter or word.BHSverse != words[
                    0].BHSverse:
                raise ValueError("All words must be in the same verse")
        self.book = words[0].BHSbook
        self.chapter = words[0].BHSchapter
        self.verse_num = words[0].BHSverse

    def sort_st(self):
        self.words.sort(key=lambda x: x.BSBsort)

    def ST(self):
        ids = list()
        copy = HebrewVerse(self.words)
        copy.sort_st()
        for word in copy.words:
            ids.append(word.clauseID.strip().lower())
        ids = list(dict.fromkeys(ids))
        final = ""
        for id_ in ids:
            row = hebrew_clause_dat.get(id_, None)
            if row:
                final += row[3] + ' '
        return final

    def __hash__(self):
        return hash(self.__repr__())


@dataclass(init=False)
class GreekChapter:
    verses: list[GreekVerse]
    book: int
    chapter: int

    def __init__(self, verses):
        self.verses: list[GreekVerse] = verses
        # make sure all the verses are in the same chapter and book
        for verse in verses:
            if verse.book != verses[0].book or verse.chapter != verses[0].chapter:
                raise ValueError("All verses must be in the same chapter")
        self.book = verses[0].book
        self.chapter = verses[0].chapter

    def __hash__(self):
        return hash(self.__repr__())


@dataclass(init=False)
class HebrewChapter:
    verses: list[HebrewVerse]
    book: int
    chapter: int

    def __init__(self, verses):
        self.verses: list[HebrewVerse] = verses
        # make sure all the verses are in the same chapter and book
        for verse in verses:
            if verse.book != verses[0].book or verse.chapter != verses[0].chapter:
                raise ValueError("All verses must be in the same chapter")
        self.book = verses[0].book
        self.chapter = verses[0].chapter

    def __hash__(self):
        return hash(self.__repr__())


@mem_cache
def get_greek_chapter(book: int, chapter: int) -> GreekChapter:
    print("loading greek chapter")
    words = []
    for row in greek_dat:
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


@mem_cache
def get_hebrew_chapter(book: int, chapter: int) -> HebrewChapter:
    print("loading hebrew chapter")
    words = []
    last_sort = 0
    for row in hebrew_dat:
        word = HebrewWord(row, float(last_sort) - 0.5)
        last_sort = word.BHSwordSort
        if word.BHSbook == book and word.BHSchapter == chapter:
            words.append(word)
        elif word.BHSbook > book or (word.BHSbook == book and word.BHSchapter > chapter):
            break
    # group the words into verses
    verses = []
    cur_verse = []
    if not words:
        raise ValueError(f"Chapter {chapter} not found in book {book}")
    verse_num = words[0].BHSverse
    for word in words:
        if word.BHSverse != verse_num:
            verses.append(HebrewVerse(cur_verse))
            cur_verse = []
            verse_num = word.BHSverse
        cur_verse.append(word)
    if cur_verse:
        verses.append(HebrewVerse(cur_verse))
    return HebrewChapter(verses)


@dataclass(init=False)
class GreekStrongs:
    strongs: int
    lex: str
    translit: str
    pronunciation: str
    strongs_str: str
    kjv_def: str

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
        n = "G" + str(num)
        data = greek_strongs_dat
        if n in data:
            entry: dict = data[n]
            self.strongs = num
            self.lex = entry.get('lemma', '')
            self.translit = entry.get('translit', '')
            self.pronunciation = entry.get('pronunciation', '')
            self.derv = entry.get('derivation', '')
            self.strg = entry.get('strongs_def', '')
            self.strongs_str = ''
            if self.derv:
                self.strongs_str += f'{self.derv}'
            if self.strg:
                if self.derv:
                    self.strongs_str += f' '
                self.strongs_str += f'{self.strg}'
            self.kjv_def = entry.get('kjv_def', '')

    def __hash__(self):
        return hash(self.__repr__())


@dataclass(init=False)
class HebrewStrongs:
    strongs: int
    lex: str
    translit: str
    pronunciation: str
    strongs_str: str
    kjv_def: str

    def __init__(self, number):
        if isinstance(number, int):
            num = number
        elif isinstance(number, str):
            if number[0] == 'H':
                num = int(number[1:])
            else:
                num = int(number)
        else:
            raise ValueError("Invalid input")

        n = 'H' + str(num)
        data = hebrew_strongs_dat
        if n in data:
            entry: dict = data[n]
            self.strongs = num
            self.lex = entry.get('lemma', '')
            self.translit = entry.get('xlit', '')
            self.pronunciation = entry.get('pron', '')
            self.derv = entry.get('derivation', '')
            self.strg = entry.get('strongs_def', '')
            self.strongs_str = ''
            if self.derv:
                self.strongs_str += f'{self.derv}'
            if self.strg:
                if self.derv:
                    self.strongs_str += f' '
                self.strongs_str += f'{self.strg}'
            self.kjv_def = entry.get('kjv_def', '')
        else:
            self.strongs = num
            self.lex = ''
            self.translit = ''
            self.pronunciation = ''
            self.strongs_str = ''
            self.kjv_def = ''


def get_strongs(number, debug=None):
    if isinstance(number, str):
        if len(number) == 0:
            if debug is not None:
                print(debug)
            raise ValueError("Invalid input")
        if number[0] == "G":
            return GreekStrongs(number)
        elif number[0] == "H":
            return HebrewStrongs(number)
        else:
            if debug is not None:
                print(debug)
            raise ValueError("Invalid input")


def get_chapter(book: int, chapter: int):
    if is_new_testament(book):
        return get_greek_chapter(book, chapter)
    else:
        return get_hebrew_chapter(book, chapter)


def is_new_testament(book):
    if isinstance(book, int):
        return 39 < book < 67
    elif isinstance(book, str):
        if book.isdigit():
            return 39 < int(book) < 67
        else:
            return book.capitalize().strip() in ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians',
                                                 '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians',
                                                 '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy',
                                                 'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter',
                                                 '1 John', '2 John', '3 John', 'Jude', 'Revelation']
    return False


def get_book_names():
    return ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua', 'Judges', 'Ruth', '1 Samuel',
            '2 Samuel', '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job',
            'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel',
            'Daniel', 'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai',
            'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians',
            '2 Corinthians', 'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians',
            '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter',
            '1 John', '2 John', '3 John', 'Jude', 'Revelation']


def get_book_sizes():
    return [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12,
            14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5,
            5, 3, 5, 1, 1, 1, 22]


@mem_cache
def to_html(ch):
    print("building html...")
    main = ""
    for verse in ch.verses:
        main += f"""<span class="verse" id="verse{verse.verse_num}"><b>{verse.verse_num}</b> {verse.ST()}</span>"""
    return main
