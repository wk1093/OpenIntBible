
from flask import Flask, render_template, request

from fcache import cache

import bible_api


app = Flask(__name__)

@app.route('/')
def index():
    dark_mode = False
    if request.args.get('dark') is not None and request.args.get('dark') != "0":
        dark_mode = True
    book_sizes = bible_api.get_book_sizes()
    books = bible_api.get_book_names()
    return render_template('index.html', is_new_testament=bible_api.is_new_testament, book_enum=enumerate(books), dark_mode=dark_mode, book_sizes=book_sizes)

@app.route('/ch/<int:book>/<int:chapter>')
def chapter(book, chapter):
    dark_mode = False
    if request.args.get('dark') is not None and request.args.get('dark') != "0":
        dark_mode = True
    selected_verse = request.args.get('verse')
    selected_word = request.args.get('word')
    # if none is selected, select the first verse in a new request
    if selected_verse is None:
        # redirect to this same link, but with ?verse=1
        return f"""<script>window.location.href = '/ch/{book}/{chapter}?verse=1&word=0'</script>"""

    if selected_word is None:
        return f"""<script>window.location.href = '/ch/{book}/{chapter}?verse={selected_verse}&word=0'</script>"""

    sel_verse = int(selected_verse)
    sel_word = int(selected_word)

    # these 2 functions are slow, so we cache them
    # check if we have a miss, if so, return a loading page
    gch = bible_api.get_greek_chapter(book, chapter)

    main = bible_api.to_html(gch)

    verse = None
    for v in gch.verses:
        if v.verse_num == sel_verse:
            verse = v
            break
    if verse is None:
        return "<h1>An Error Occurred</h1><p>Verse not found</p>"

    books = bible_api.get_book_names()
    book_sizes = bible_api.get_book_sizes()

    book_name = books[book-1]

    return render_template('ch.html', book=book, chapter=chapter, dark_mode=dark_mode, book_enum=enumerate(books), main=main, sel_verse=sel_verse, sel_word=sel_word, book_sizes=book_sizes, book_name=book_name, is_new_testament=bible_api.is_new_testament)

@app.route('/left/<int:book>/<int:chapter>/<int:verse>')
def left(book, chapter, verse):
    dark_mode = False
    if request.args.get('dark') is not None and request.args.get('dark') != "0":
        dark_mode = True
    selected_word = request.args.get('word')
    if selected_word is None:
        return f"""<script>window.location.href = '/left/{book}/{chapter}/{verse}?word=0'</script>"""

    sel_word = int(selected_word)

    gch = bible_api.get_greek_chapter(book, chapter)
    vs = None
    for v in gch.verses:
        if v.verse_num == verse:
            vs = v
            break
    if vs is None:
        return "<h1>An Error Occurred</h1><p>Verse not found</p>"

    vs.sort_st()

    book_name = bible_api.get_book_names()[book-1]

    return render_template('left.html', book=book, chapter=chapter, verse=verse, dark_mode=dark_mode, words_enum=enumerate(vs.words),
                           sel_word=sel_word, book_name=book_name, is_new_testament=bible_api.is_new_testament)

@app.route('/bottom/<int:book>/<int:chapter>/<int:verse>/<int:word>')
def bottom(book, chapter, verse, word):
    dark_mode = False
    if request.args.get('dark') is not None and request.args.get('dark') != "0":
        dark_mode = True
    # strongs definition and other details about the word
    # for now just put the lexeme and other info
    gch = bible_api.get_greek_chapter(book, chapter)
    vs = None
    for v in gch.verses:
        if v.verse_num == verse:
            vs = v
            break
    if vs is None:
        return "An error occurred"
    w = vs.words[word]
    s = bible_api.StrongsDefinition(w.sn)

    return render_template('bottom.html', book=book, chapter=chapter, verse=verse, word=word, dark_mode=dark_mode, w=w, s=s)


if __name__ == '__main__':
    # app.run(debug=True)
    # cache the entire bible
    print("Caching the entire Bible...")
    for book in range(40, 67):
        for chapter in range(1, bible_api.get_book_sizes()[book-1]+1):
            print(f"Caching {bible_api.get_book_names()[book-1]} {chapter}")
            bible_api.to_html(bible_api.get_greek_chapter(book, chapter))