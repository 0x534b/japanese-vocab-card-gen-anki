import json
import requests
from urllib.parse import quote

import anki

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

API_URI = 'https://jisho.org/api/v1/search/words'
API_PARAM = 'keyword'
ADD_ERRORS = {
    0: "Success",
    1: "Note Exists",
    2: "Not Found",
    3: "Connection Error"
}
MODEL_NAME = 'Jisho-Japanese'

def create_model(models):
    model = models.new(MODEL_NAME)

    models.addField(model,{
            'name': 'Vocabulary-Kanji',
            'ord': 0,
            'sticky': False,
            'rtl': False,
            'font': 'ＭＳ ゴシック',
            'size': 12,
            'media': []
        })

    models.addField(model,{
            'name': 'Vocabulary-Kana',
            'ord': 1,
            'sticky': False,
            'rtl': False,
            'font': 'ＭＳ ゴシック',
            'size': 12,
            'media': []
        })

    models.addField(model,{
            'name': 'Vocabulary-English',
            'ord': 2,
            'sticky': False,
            'rtl': False,
            'font': 'ＭＳ ゴシック',
            'size': 12,
            'media': []
        })

    model['css'] = '.card {\n font-family: arial;\n font-size: 25px;\n text-align: center;\n color: White;\n background-color: Black;\n}'
    model['latexPre'] = '\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n'

    template = models.new_template('English Translate')
    template['qfmt'] = '<span style="font-size: 50px;  ">{{Vocabulary-Kanji}}</span>'
    template['afmt'] = '{{FrontSide}}\n \n<hr id=answer>\n \n<span style="font-size: 30px; ">{{Vocabulary-English}}</span>\n<br>\n<span style="font-size: 35px; ">{{Vocabulary-Kana}}</span>\n<br>\n'

    models.addTemplate(model, template)

    models.add(model)

    return model

def mkBtn(txt, f, parent):
    b = QPushButton(txt)
    b.clicked.connect(f)
    parent.addWidget(b)
    return b

class AddWord(QDialog):
    def __init__(self, ID, parent=None):
        super(AddWord, self).__init__(parent)
        self.mw = parent
        self.word_info = None
        self.deck_id = ID
        self.setWindowTitle('Type your word')
        self.grid = grid = QGridLayout(self)
        self.vbox = vbox = QVBoxLayout()

        # Give me the word
        self.word_in = QLineEdit()
        vbox.addWidget(self.word_in)

        # List the info
        self.info = QListWidget()
        vbox.addWidget(self.info)

        # Search
        self.showABtn = mkBtn('Search Jisho', self.search, vbox)

        # Add Card
        self.showABtn = mkBtn('Add Card', self.add, vbox)

        # layout
        grid.addLayout(vbox, 0, 0)

    def search(self):
        self.info.clear()
        word = self.word_in.text().strip()

        if word != '':
            encoded = quote(word)
            r = requests.get(f'{API_URI}?{API_PARAM}={encoded}')
        
            if r.status_code == requests.codes.ok:
                data = json.loads(r.text)

                if len(data) > 0:
                    self.word_info = {
                        'word': data['data'][0]['japanese'][0].get('word', word),
                        'reading': data['data'][0]['japanese'][0]['reading'],
                        'senses': data['data'][0]['senses']
                    }
                    self.info.insertItem(0, f"word: {self.word_info['word']}")
                    self.info.insertItem(1, f"reading: {self.word_info['reading']}")
                    self.info.insertItem(2,
                        f"translations: {'; '.join([', '.join(s['english_definitions']) for s in self.word_info['senses']])}")
                else:
                    showInfo("Word not found.")
    def add(self):
        if self.word_info is not None:
            # TODO: lazy
            exist = mw.col.find_notes(self.word_info['word'])

            if len(exist) == 0:
                nt = mw.col.models.by_name(MODEL_NAME)

                if nt is None:
                    nt = create_model(mw.col.models)

                note = anki.notes.Note(col=mw.col,model=nt)
                note['Vocabulary-Kanji'] = self.word_info['word']
                note['Vocabulary-Kana'] = self.word_info['reading']
                note['Vocabulary-English'] = ''.join([f"{i+1}. {', '.join(s['english_definitions'])}<br><br>" for i,s in enumerate(self.word_info['senses'])])
                mw.col.add_note(note, self.deck_id)
                mw.reset()
                self.info.clear()
                self.word_info = None
            else:
                showInfo(f'Word: "{self.word_info["word"]}" already in deck.')

class ChooseDeck(QDialog):
    def __init__(self, parent=None):
        super(ChooseDeck, self).__init__(parent)
        self.chosen = None
        self.mw = parent
        self.setWindowTitle('Choose a Deck')
        self.grid = grid = QGridLayout(self)
        self.vbox = vbox = QVBoxLayout()

        self.showABtn = mkBtn('Add Card', self.add_manual, vbox)
        self.showABtn = mkBtn('Add From File', self.add_file, vbox)

        # Display
        vbox.addSpacing(40)

        # List the decks
        self.deck_list = QListWidget()
        self.decks = mw.col.decks.all_names_and_ids()
        self.deck_list.insertItems(0, [deck.name for deck in self.decks])
        self.deck_list.clicked.connect(self.deck_chosen)
        vbox.addWidget(self.deck_list)

        # layout
        grid.addLayout(vbox, 0, 0)

    def deck_chosen(self, idx):
        self.chosen = idx

    def add_manual(self):
        if self.chosen is not None:
            deck_id = self.decks[self.chosen.row()].id
            mw.ac = AddWord(deck_id, self.mw)
            mw.ac.show()

    def add_file(self):
        if self.chosen is not None:
            deck_id = self.decks[self.chosen.row()].id
            addFromFile(deck_id)

class AddReport(QDialog):
    def __init__(self, results, parent=None):
        super(AddReport, self).__init__(parent)
        self.mw = parent
        self.setWindowTitle('Import Complete')
        self.grid = grid = QGridLayout(self)
        self.vbox = vbox = QVBoxLayout()

        successful = len(results[0])
        failed = sum([len(results[key]) for key in results.keys() if key != 0])
        self.win = QLabel()
        self.win.setText(f'Successful: {successful}\r\nFailed: {failed}')
        vbox.addWidget(self.win)

        # Display
        vbox.addSpacing(40)

        self.table = QTableWidget()
        self.table.setRowCount(max([len(results[r]) for r in results])+1)
        self.table.setColumnCount(len(ADD_ERRORS))

        for k in ADD_ERRORS.keys():
            self.table.setItem(0, k, QTableWidgetItem(ADD_ERRORS[k]))

            for i,w in enumerate(results[k]):
                self.table.setItem(i+1, k, QTableWidgetItem(w))

        vbox.addWidget(self.table)

        # layout
        grid.addLayout(vbox, 0, 0)

def wordAdd():
    mw.cd = ChooseDeck(mw)
    mw.cd.show()

def tryAddCard(word, deck_id):
    word_info = None

    if word != '':
        encoded = quote(word)

        # try 5 times
        for i in range(5):
            r = requests.get(f'{API_URI}?{API_PARAM}={encoded}')
            if r.status_code == requests.codes.ok:
                break
        else:
            return 3

        data = json.loads(r.text)
        if len(data) > 0:
            word_info = {
                'word': data['data'][0]['japanese'][0].get('word', word),
                'reading': data['data'][0]['japanese'][0]['reading'],
                'senses': data['data'][0]['senses']
            }
            dn = mw.col.decks.name(deck_id)
            exist = mw.col.find_notes(f'deck:"{dn}" AND Vocabulary-Kanji:"{word_info["word"]}"')
            if len(exist) == 0:
                nt = mw.col.models.byName("Japanese-75658")
                note = anki.notes.Note(col=mw.col,model=nt)
                note['Vocabulary-Kanji'] = word_info['word']
                note['Vocabulary-Kana'] = word_info['reading']
                note['Vocabulary-English'] = ''.join([f"{i+1}. {', '.join(s['english_definitions'])}<br><br>" for i,s in enumerate(word_info['senses'])])
                mw.col.add_note(note, deck_id)
                mw.reset()
                return 0
            else:
                return 1
        else:
            return 2

def addFromFile(deck_id):
    filename, _ = QFileDialog.getOpenFileName(mw, "Choose a word list.", "", "Text Files (*.txt);;All Files (*)")
    # showInfo(filename)
    if filename:
        results = {}

        with open(filename, 'rb') as f:
            data = f.read()
            words = [word.decode('utf-8').strip() for word in data.split(b'\r\n')]
            words = list(filter(None, words))

        results = {}
        for key in ADD_ERRORS.keys():
            results[key] = []
        for word in words:
            if word.startswith('//'):
                continue
            err = tryAddCard(word, deck_id)
            results[err].append(word)

        mw.ar = AddReport(results, mw)
        mw.ar.show()
    else:
        showInfo("File not found.")

def addMenu():
    # add actions
    a = QAction(mw)
    a.setText("Add Words")
    # Call from lambda to preserve default argument
    qconnect(a.triggered, lambda: wordAdd())
    mw.form.menuTools.addAction(a)

addMenu()
