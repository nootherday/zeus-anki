from gsheets import Sheets

import os, glob

class ZeusDB():
    def __init__(self, config):
        self._config = config

    def sync(self):
        sheets = Sheets.from_files(self._config["gsheets_secrets"], self._config["gsheets_storage"])
        s = sheets.get(self._config["url"])
        path = self._config["path"]

        for f in glob.glob(os.path.join(path, "*.csv")):
            os.remove(f)

        s.to_csv(make_filename=os.path.join(path, "%(sheet)s.csv"))

if __name__ == "__main__":
    import json

    with open('config.json', 'r') as f:
        config = json.load(f)

        db = ZeusDB(config["db"])
        db.sync()