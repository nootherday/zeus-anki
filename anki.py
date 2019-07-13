from tts import ZeusTTS
from db import ZeusDB

import genanki

import csv
import os
import json

class ZeusAnki():
    def __init__(self, config_filename):
        with open(config_filename, 'r') as f:
            self._config = json.load(f)

        self._tts = ZeusTTS(self._config["tts"])


        self._model = {}
        self._model["default"] = genanki.Model(
            2004387350,
            'zeus model',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
                },
            ]
        )
        self._model["tts"] = genanki.Model(
            1939171148,
            'zeus tts model',
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'MyMedia'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}<br>{{MyMedia}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
                },
            ]
        )

    def gen_deck(self, csv_filename):
        name = os.path.splitext(os.path.basename(csv_filename))[0]
        deck = genanki.Deck(int(abs(hash(name)) / 100000000), name)
        media_files = []
        with open(csv_filename) as csv_file:
            for row in csv.reader(csv_file):
                if len(row) != 2:
                    continue
                q = row[0].strip()
                a = row[1].strip()
                if len(q) == 0 or len(a) == 0:
                    continue

                audio = self._tts.generate(q)
                if audio is not None:
                    audio_name = os.path.basename(audio)
                    note = genanki.Note(model=self._model["tts"], fields=[q, a, f"[sound:{audio_name}]"])
                    media_files.append(audio)
                else:
                    note = genanki.Note(model=self._model["default"], fields=[q, a])
                deck.add_note(note)

        return deck, media_files

    def gen_decks(self):
        db = ZeusDB(self._config["db"])
        sheets = db.sync()
        total_media_files = []
        decks = []

        for sheet in sheets:
            deck, media_files = self.gen_deck(sheet)
            total_media_files.extend(media_files)
            decks.append(deck)

        package = genanki.Package(decks)
        package.media_files = total_media_files
        package.write_to_file(self._config["output"])

if __name__ == "__main__":
    anki = ZeusAnki("config.json")
    anki.gen_decks()
