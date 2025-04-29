from typing import Optional
import time
from setting import LANG_JP, LANG_EN, LANG_ZH, LANG_TW, SUPPORTED_LANG_CODES
from recognizer import StreamingRecognizer
from recorder import AudioRecorder

class Language:
    def __init__(self, lang_code, api_lang, direct_mapping):
        self.lang_code = lang_code
        self.api_lang = api_lang
        self.direct_mapping = direct_mapping

    def __repr__(self):
        return f"Language(lang_code={self.lang_code}, api_lang={self.api_lang}, direct_mapping={self.direct_mapping})"

LANGUAGE_MODELS = {
    "ja": Language(
        lang_code=LANG_JP,
        api_lang="Japanese",
        direct_mapping={
            "うえ": "up",
            "上": "up",
            "した": "down",
            "下": "down",
            "左": "left",
            "右": "right"
        }
    ),
    "en": Language(
        lang_code=LANG_EN,
        api_lang="English",
        direct_mapping={
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right"
        }
    ),
    "zh-TW": Language(
        lang_code=LANG_ZH,
        api_lang="STT for course",
        direct_mapping={
            "上": "up",
            "上面": "up",
            "下": "down",
            "下面": "down",
            "左": "left",
            "左邊": "left",
            "右": "right",
            "右邊": "right"
        }
    ),
    "ta": Language(
        lang_code=LANG_TW,
        api_lang="TA Phoneme",
        direct_mapping={
            "t-ing* p-ing*": "up",
            "t-ing* k-uan*": "up",
            "e* b-in*": "down",
            "e* kh-a*": "down",
            "t-o* p-ing*": "left",
            "t-o* tsh-iu* p-ing*": "left",
            "ts-iann* tsh-iu* p-ing*": "right",
            "ts-iann* p-ing*": "right"
        }
    )
}

def detect_language(audio_recorder: Optional[AudioRecorder] = None, timeout_seconds: float = 30.0) -> Optional[Language]:
    """
    啟動多語言辨識器，檢查語音內容是否包含語言名稱（如「中文」、「English」）。
    若為中文或英語，回傳對應的 Language 物件，否則回傳 None。
    超過 timeout 或無有效語音也回傳 None。
    """
    stop_record = False
    if audio_recorder is None:
        stop_record = True
        audio_recorder = AudioRecorder()
        audio_recorder.start()
    
    supported_languages = [
        lang for lang in LANGUAGE_MODELS.values() if lang.lang_code in SUPPORTED_LANG_CODES
    ]
    recognizers = [
        StreamingRecognizer(audio_recorder=audio_recorder, language=lang.api_lang)
        for lang in supported_languages
    ]

    # 語言名稱映射
    language_names = {
        "中文": "zh-TW",
        "國語": "zh-TW",
        "English": "en",
        "日本語": "ja",
        "t-ai* g-i*": "ta"
    }

    # 同時啟動辨識
    for rec in recognizers:
        rec.start()

    detected_lang = None
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        for lang, rec in zip(supported_languages, recognizers):
            if rec.result is not None and rec.result != "<{silent}>":
                # 檢查語音內容是否包含語言名稱
                for name, lang_code in language_names.items():
                    if name in rec.result:
                        detected_lang = LANGUAGE_MODELS.get(lang_code)
                        break
                break
        if detected_lang:
            break

    for rec in recognizers:
        rec.stop()

    if stop_record:
        audio_recorder.stop()
    
    return detected_lang