import base64
import requests
import time
from typing import Optional
from .classes import Language


class Recognizer:
    def __init__(self, language: Language):
        self.language = language
        self.api_url = "http://140.116.245.149:5002/proxy"
        self.token = "2025@ME@asr"

    def recognize(self, wav_path: str) -> Optional[str]:
        with open(wav_path, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        payload = {
            'lang': self.language.api_lang,
            'token': self.token,
            'audio': audio_base64
        }

        for _ in range(3):
            try:
                response = requests.post(self.api_url, data=payload, timeout=10)
                if response.status_code == 200:
                    return response.json().get('sentence', "<{silent}>")
            except requests.RequestException:
                time.sleep(1)
        return "<{silent}>"


def recognize_direct(recorder, recognizer: Recognizer) -> int:
    """return direct_code:int"""
    while True:
        wav_file = recorder.record_speech()
        if not wav_file:
            continue

        result = recognizer.recognize(wav_file).lower().strip('.!? ')
        if result != "<{silent}>":
            direct_code = recognizer.language.direct_mapping.get(result)
            if direct_code is not None:
                return direct_code
            raise ValueError("辨識結果不在指定範圍內")
