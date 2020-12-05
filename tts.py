import boto3
from pydub import AudioSegment

import sys
import os
import re
import hashlib

def get_filename(text):
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()[:5]
    return re.sub("[^a-z]", "_", text.lower())[:20] + "_" + h + ".mp3"

class ZeusTTS():
    def __init__(self, config):
        session = boto3.Session(
            aws_access_key_id = config['aws_access_key_id'],
            aws_secret_access_key = config['aws_secret_access_key'])
        self._voice_ids = config["voice_ids"]
        self._interval_in_seconds = config["interval_in_seconds"]
        self._path = os.path.abspath(config["path"])
        self._polly = session.client('polly', region_name=config["aws_region"])

    def generate(self, text):
        if re.search('[a-zA-Z]', text) is None:
            return None

        filename = os.path.join(self._path, get_filename(text))

        if os.path.exists(filename):
            return filename

        print (f"generate {text}")

        temp_filename = os.path.join(self._path, "_temp.mp3")
        audio = None

        for voice_id in self._voice_ids:
            response = self._polly.synthesize_speech(
                Engine = 'neural',
                LanguageCode = 'en-US',
                VoiceId = voice_id,
                TextType = 'text',
                OutputFormat = 'mp3', 
                Text = f'{text}')
                # TextType = 'ssml',
                # Text = f'<speak><prosody rate="slow">{text}</prosody></speak>')
                

            file = open(temp_filename, 'wb')
            file.write(response['AudioStream'].read())
            file.close()

            for i in range(2):
                cur = AudioSegment.from_mp3(temp_filename)
                if audio == None:
                    audio = cur
                else:
                    audio = audio + AudioSegment.silent(duration=self._interval_in_seconds * 1000) + cur

        audio.export(filename, format="mp3")
        os.remove(temp_filename)

        return filename

if __name__ == "__main__":
    import json

    with open('config.json', 'r') as f:
        config = json.load(f)

        tts = ZeusTTS(config["tts"])
        tts.generate("my test")