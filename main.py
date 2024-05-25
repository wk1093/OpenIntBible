"""
OpenIntBible - An Open-Source Interlinear Bible App for Windows, Mac, Linux, Android, and Web

This is a web Python app that uses Flask to serve the OpenIntBible web app.

"""
from flask import Flask, render_template, request

from functools import cache


import bible_api


app = Flask(__name__)

@app.route('/')
def index():
    return """
<h1>OpenIntBible</h1>
<p>An Open-Source Interlinear Bible App for Windows, Mac, Linux, Android, and Web</p>
<p>As of now, only Greek is supported (so only New Testament), but Hebrew and Old Testament support is planned.</p>
<a href="/ch/40/1">Matthew 1</a>
"""

@cache
def to_html(verses):
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

    main = to_html(gch)

    left = "<h2>An Error Occurred</h2>"
    # left will contain each greek word
    verse = None
    for v in gch.verses:
        if v.verse_num == sel_verse:
            verse = v
            break
    if verse is not None:
        left = f"<iframe src='/left/{book}/{chapter}/{sel_verse}?word={sel_word}{'&dark=1' if dark_mode else '&dark=0'}' width='100%' height='100%' style=\"visibility:hidden;\" onload=\"this.style.visibility='visible';\"></iframe>"

    # bottom
    bottom = "<h2>An Error Occurred</h2>"
    if verse is not None:
        bottom = f"<iframe src='/bottom/{book}/{chapter}/{sel_verse}/{sel_word}{'?dark=1' if dark_mode else '?dark=0'}' width='100%' height='100%' style=\"visibility:hidden;\" onload=\"this.style.visibility='visible';\"></iframe>"

    books = bible_api.get_book_names()
    book_sizes = bible_api.get_book_sizes()

    # selects = " ".join([f'<option value="{i+1}" {"selected" if i+1 == book else ""}>{name}</option>' for i, name in enumerate(books)])
    # we need to remove the Old Testament books
    selects = ""
    for i, name in enumerate(books):
        if bible_api.is_new_testament(i+1):
            selects += f'<option value="{i+1}" {"selected" if i+1 == book else ""}>{name}</option>'


    light_css = f"""
.verse {{
    display: block;
    padding: 10px;
    border-bottom: 1px solid #dfdfdf;
}}

.verse.selected {{
    background-color: #f0f0f0;
}}

.iframe {{
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
}}

select {{
    height: 1.8rem;
    width: max-content;
    margin: 2px;
    border: 1px solid #dfdfdf;
    background-color: white;
    color: black;
}}

#nav {{
    display: flex;
    align-items: center;
    padding: 5px;
    border-bottom: 1px solid #dfdfdf;
    background-color: white;
}}

input {{
    height: 1rem;
    padding: 5px;
    margin: 2px;
    border: 1px solid #dfdfdf;
    background-color: white;
    color: black;
}}

button {{
    height: 1.8rem;
    padding: 5px;
    margin: 2px;
    border: 1px solid #dfdfdf;
    background-color: white;
    color: black;
}}
"""

    dark_css = f"""
body, html {{
    background-color: #333;
    color: white;
}}

.verse {{
    display: block;
    padding: 10px;
    border-bottom: 1px solid #555;
    background-color: #222;
}}

.verse.selected {{
    background-color: #555;
}}

div {{
    color: white;
    background-color: #333;
}}

select {{
    height: 1.8rem;
    width: max-content;
    padding: 5px;
    margin: 2px;
    border: 1px solid #555;
    background-color: #222;
    color: white;  
}}

#nav {{
    display: flex;
    align-items: center;
    padding: 5px;
    border-bottom: 1px solid #555;
    background-color: #222;
}}

input {{
    height: 1rem;
    padding: 5px;
    margin: 2px;
    border: 1px solid #555;
    background-color: #222;
    color: white;
}}

button {{
    height: 1.8rem;
    padding: 5px;
    margin: 2px;
    border: 1px solid #555;
    background-color: #222;
    color: white;  
}}

iframe {{
    background-color: #333;
    color: white;
}}
"""

    css = dark_css if dark_mode else light_css

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>OpenIntBible {book} {chapter}</title>
    <link rel="stylesheet" type="text/css" href="https://rawgit.com/vitmalina/w2ui/master/dist/w2ui.min.css">
    <meta name="color-scheme" content="{'dark' if dark_mode else 'light'}">
    <style type="text/css">
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        
        iframe {{
            border: none;
        }}

        #layout {{
            min-height: 100%; 
        }}
        
    {css}
    
    button#dark {{
        margin-left: auto;
    }}
        
    </style>
    <!--[if lte IE 6]>
    <style type="text/css">
        #layout {{
            height: 100%;
        }}
    </style>
    <![endif]-->
</head>
<body>

<div id="nav">
    <form id="form">
    <select id="book">
        {selects}
    </select>
    <input type="number" id="chapter" min="1" value="{chapter}">
    <button id="go">Go</button>
    </form>
    <button id="dark">Toggle Dark Mode</button>
</div>
<div id="layout"></div>

<script type="module">
import {{ w2layout }} from 'https://rawgit.com/vitmalina/w2ui/master/dist/w2ui.es6.min.js'

let pstyle = 'border: 1px solid {'#dfdfdf' if not dark_mode else '#555'}; padding: 5px; {'' if not dark_mode else 'background-color: #333; color: white;'}'
let astyle = 'border: 1px solid {'#dfdfdf' if not dark_mode else '#555'}; padding: 5px; overflow: hidden; {'' if not dark_mode else 'background-color: #333; color: white;'}'
var layout = new w2layout({{
    box: '#layout',
    name: 'layout',
    padding: 4,
    panels: [
        {{ type: 'left', size: 400, resizable: true, style: astyle, html: '<h2>Left</h2>' }},
        {{ type: 'main', style: pstyle, html: '<h2>Main</h2>' }},
        {{ type: 'bottom', size: 400, resizable: true, style: astyle, html: '<h2>Bottom</h2>' }},
        {{ type: 'top', size: 50, resizable: false, style: astyle, html: '<h2>Top</h2>' }}
    ]
}})

layout.html('left', `{left}`)
layout.html('main', `{main}`)
layout.html('bottom', `{bottom}`)
// copy the nav bar to the top
layout.html('top', document.querySelector('#nav').outerHTML)
// remove the old nav bar
document.querySelector('#nav').remove()



// when clicking on a verse, redirect to the same page but with the verse number
document.querySelectorAll('.verse').forEach(verse => {{
    verse.addEventListener('click', () => {{
        window.location.href = '/ch/{book}/{chapter}?verse=' + verse.id.replace('verse', '') + '&word=0{'&dark=1' if dark_mode else '&dark=0'}'
    }})
}})

// save scroll position of the verses panel
// div#layout_layout_panel_main div.w2ui-panel-content
let mainPanel = document.querySelector('div#layout_layout_panel_main div.w2ui-panel-content')
let scrollPos = sessionStorage.getItem('p0_scrollPos')
let book = sessionStorage.getItem('p0_book')
let chapter = sessionStorage.getItem('p0_chapter')
if (scrollPos && book === '{book}' && chapter === '{chapter}') {{
    mainPanel.scrollTop = scrollPos
}}

// save scroll position when leaving the page
window.addEventListener('beforeunload', () => {{
    sessionStorage.setItem('p0_scrollPos', mainPanel.scrollTop)
    sessionStorage.setItem('p0_book', {book})
    sessionStorage.setItem('p0_chapter', {chapter})
}})


// give the selected verse number the selected class
document.querySelectorAll('.verse').forEach(verse => {{
    if (verse.id === 'verse{sel_verse}') {{
        verse.classList.add('selected')
    }}
}})

// enforce book_sizes
let bookSizes = {book_sizes}
document.querySelector('#book').addEventListener('change', () => {{
    let book = document.querySelector('#book').value
    // set max chapter to the book size
    document.querySelector('#chapter').setAttribute('max', bookSizes[book])
    
}})

// form
document.querySelector('#form').addEventListener('submit', (e) => {{
    e.preventDefault()
    let book = document.querySelector('#book').value
    let chapter = document.querySelector('#chapter').value
    if (chapter > bookSizes[book]) {{
        chapter = bookSizes[book]
    }}
    window.location.href = `/ch/${{book}}/${{chapter}}?verse=1&word=0{'&dark=1' if dark_mode else '&dark=0'}`
}})

document.querySelector('#dark').addEventListener('click', () => {{
    window.location.href = `/ch/{book}/{chapter}?verse={sel_verse}&word={sel_word}{'&dark=0' if dark_mode else '&dark=1'}`
}})
    


</script>

</body>
</html>
"""

@app.route('/left/<int:book>/<int:chapter>/<int:verse>')
def left(book, chapter, verse):
    dark_mode = False
    if request.args.get('dark') is not None and request.args.get('dark') != "0":
        dark_mode = True
    selected_word = request.args.get('word')
    if selected_word is None:
        return f"""<script>window.location.href = '/left/{book}/{chapter}/{verse}?word=0'</script>"""

    sel_word = int(selected_word)

    light_css = f"""
p {{
    padding: 5px;
    margin: 0;
    border-bottom: 1px solid #dfdfdf;
}}

p.selected {{
    background-color: #f0f0f0;
}}
    """
    dark_css = f"""
body, html {{
    background-color: #333;
    color: white;
}}

p {{
    padding: 5px;
    margin: 0;
    border-bottom: 1px solid #555;
    background-color: #222;
}}

p.selected {{
    background-color: #555;
}}

div {{
    color: white;
    background-color: #333;
}}
    """

    css = dark_css if dark_mode else light_css


    gch = bible_api.get_greek_chapter(book, chapter)
    vs = None
    for v in gch.verses:
        if v.verse_num == verse:
            vs = v
            break
    if vs is not None:
        left = ""
        i = 0
        for word in vs.words:
            if i == sel_word:
                left += f"<p class=\"selected\">{word.ST} => {word.transSBLcap} ({word.TBESG})</p>"
            else:
                left += f"<p>{word.ST} => {word.transSBLcap} ({word.TBESG})</p>"
            i += 1
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>OpenIntBible {book} {chapter}:{verse}</title>
    <meta name="color-scheme" content="{'dark' if dark_mode else 'light'}">
    <style type="text/css">
        html, body {{
            height: 100%;
            margin: 0;
        }}
        
        {css}
        
    </style>
</head>
<body>
{left}
<script>

// when clicking on a word, redirect to the same page but with the word number
// we can't directly just redirect, because we are an iframe
document.querySelectorAll('p').forEach((word, index) => {{
    word.addEventListener('click', () => {{
        window.parent.location.href = '/ch/{book}/{chapter}?verse={verse}&word=' + index {"+ '&dark=1'" if dark_mode else "+ '&dark=0'"}
    }})
}})

// scroll saver
let scrollPos = sessionStorage.getItem('p1_scrollPos')
let book = sessionStorage.getItem('p1_book')
let chapter = sessionStorage.getItem('p1_chapter')
let verse = sessionStorage.getItem('p1_verse')

if (scrollPos && book === '{book}' && chapter === '{chapter}' && verse === '{verse}') {{
    window.scrollTo(0, scrollPos)
}}

window.addEventListener('beforeunload', () => {{
    sessionStorage.setItem('p1_scrollPos', window.scrollY)
    sessionStorage.setItem('p1_book', {book})
    sessionStorage.setItem('p1_chapter', {chapter})
    sessionStorage.setItem('p1_verse', {verse})
}})


</script>
</body>
    """
    return "An error occurred"

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

    dark_css = f"""
body, html {{
    background-color: #333;
    color: white;
}}

h2, h3, p {{
    color: white;
}}

div {{
    color: white;
    background-color: #333;
}}
    """

    css = dark_css if dark_mode else ""

    # pad containers left and right
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>OpenIntBible {book} {chapter}:{verse}</title>
    <meta name="color-scheme" content="{'dark' if dark_mode else 'light'}">
    <style type="text/css">
        html, body {{
            height: 100%;
            margin: 0;
        }}
        
        .container {{
            padding: 5px 10px;
        }}
        
        {css}
    </style>
</head>
<body>
<div class="container">
<h2><b>{w.transSBLcap}</b> ({w.lexeme}) {w.sn} ({s.greek})</h2>
<p><b>Pronounciation:</b> {s.pronunciation}</p>
<h3>Brief Definition</h3>
<p>{w.TBESG}</p>
<h3>Strong's Definition</h3>
<p>{s.strongs_def}</p>
</div>
</body>
</html>
"""


if __name__ == '__main__':
    app.run(debug=True)