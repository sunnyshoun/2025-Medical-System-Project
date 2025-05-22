import time
import base64
import requests
from typing import Optional
from settings import SPEECH_API_TOKEN, SPEECH_API_URL
from .model import Language
from .recorder import audio_recorder

def recognize(wav_path: str, language: Language) -> Optional[str]:
        with open(wav_path, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode()
        payload = {
            'lang': language.api_lang,
            'token': SPEECH_API_TOKEN,
            'audio': audio_base64
        }

        for _ in range(3):
            try:
                response = requests.post(SPEECH_API_URL, data=payload, timeout=10)
                if response.status_code == 200:
                    return response.json().get('sentence', "<{silent}>")
            except requests.RequestException:
                time.sleep(1)
        return "<{silent}>"

def recognize_direct(language: Language) -> int:
    """return direct_code:int"""
    while True:
        wav_file = audio_recorder.record_speech()
        if not wav_file:
            continue

        result = recognize(wav_file, language).lower().strip('.!? ')
        if result != "<{silent}>":
            direct_code = language.direct_mapping.get(result)
            if direct_code is not None:
                return direct_code
            raise ValueError("辨識結果不在指定範圍內")
