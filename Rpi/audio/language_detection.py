import time
from setting import LANG_JP, LANG_EN, LANG_ZH, LANG_TW
from .classes import Language
from .recognizer import Recognizer
from .recorder import AudioRecorder

LANGUAGE_MODELS = {
    "ja": Language(
        lang_code=LANG_JP,
        api_lang="Japanese",
        direct_mapping={
            "うえ": 3,
            "上": 3,
            "した": 2,
            "下": 2,
            "左": 1,
            "右": 0
        }
    ),
    "en": Language(
        lang_code=LANG_EN,
        api_lang="English",
        direct_mapping={
            "up": 3,
            "down": 2,
            "left": 1,
            "right": 0
        }
    ),
    "zh-TW": Language(
        lang_code=LANG_ZH,
        api_lang="STT for course",
        direct_mapping={
            "上": 3,
            "上面": 3,
            "下": 2,
            "下面": 2,
            "左": 1,
            "左邊": 1,
            "右": 0,
            "右邊": 0,
            "yo": 0
        }
    ),
    "ta": Language(
        lang_code=LANG_TW,
        api_lang="TA Phoneme",
        direct_mapping={
            "t-ing* p-ing*": 3,
            "t-ing* k-uan*": 3,
            "e* b-in*": 2,
            "e* kh-a*": 2,
            "t-o* p-ing*": 1,
            "t-o* tsh-iu* p-ing*": 1,
            "ts-iann* tsh-iu* p-ing*": 0,
            "ts-iann* p-ing*": 0
        }
    )
}

def detect_language(audio_recorder: AudioRecorder, timeout_seconds: float = 30.0) -> Language:
    """
    錄製語音並檢查內容是否包含語言名稱（如「中文」、「English」）。
    若為中文或英語，回傳對應的 Language 物件，否則回傳 None。
    超過 timeout 或無有效語音也回傳 None。
    """

    language_names = {
        "中文": "zh-TW",
        "國語": "zh-TW",
        "English": "en",
        "英語": "en",
        "日本語": "ja",
        "t-ai* g-i*": "ta"
    }

    supported_languages = [lang for lang in LANGUAGE_MODELS.values() if lang.lang_code in [LANG_ZH, LANG_EN]]
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        wav_file = audio_recorder.record_speech(max_duration=30.0)
        if wav_file:
            for lang in supported_languages:
                recognizer = Recognizer(language=lang)
                result = recognizer.recognize(wav_file)
                if result and result != "<{silent}>":
                    for name, lang_code in language_names.items():
                        if name in result:
                            return LANGUAGE_MODELS.get(lang_code)
    raise TimeoutError("User did not respond")