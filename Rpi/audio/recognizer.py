from typing import Optional
from .recorder import AudioRecorder
from .classes import Language
import requests
import base64
import time

class Recognizer:
    def __init__(self, language: Language):
        self.language = language
        self.api_url = "http://140.116.245.149:5002/proxy"
        self.max_retries = 3
        self.retry_delay = 1.0  # Seconds

    def recognize(self, wav_path: str) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                with open(wav_path, 'rb') as f:
                    raw_audio = f.read()
                audio_data = base64.b64encode(raw_audio)
                payload = {
                    'lang': self.language.api_lang,
                    'token': '2025@ME@asr',
                    'audio': audio_data.decode()
                }
                response = requests.post(self.api_url, data=payload, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    return result.get('sentence', '<{silent}>')
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
            except Exception as e:
                print(f"語音辨識請求失敗 (嘗試 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        return "<{silent}>"

def recognize_direct(recorder: AudioRecorder, recognizer: Recognizer):
    while True:
        wav_file = recorder.record_speech(max_duration=5.0)
        if wav_file:
            lang = recognizer.language
            result = recognizer.recognize(wav_file).lower().strip('.!? ')
            if result != "<{silent}>":
                for k,v in lang.direct_mapping.items():
                    if k in result:
                        return v
                raise ValueError("User say the wrong word")