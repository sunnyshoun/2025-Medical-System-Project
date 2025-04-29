import time
from .classes import Language
from .recognizer import Recognizer
from .recorder import AudioRecorder
from setting import LANG_JP, LANG_EN, LANG_ZH, LANG_TW


LANGUAGE_MODELS = {
    "ja": Language(LANG_JP, "Japanese", {"うえ": 3, "上": 3, "した": 2, "下": 2, "左": 1, "右": 0}),
    "en": Language(LANG_EN, "English", {"up": 3, "down": 2, "left": 1, "right": 0}),
    "zh-TW": Language(LANG_ZH, "STT for course", {"上": 3, "上面": 3, "下": 2, "下面": 2, "左": 1, "左邊": 1, "右": 0, "右邊": 0, "yo": 0}),
    "ta": Language(LANG_TW, "TA Phoneme", {
        "t-ing* p-ing*": 3, "t-ing* k-uan*": 3, "e* b-in*": 2, "e* kh-a*": 2,
        "t-o* p-ing*": 1, "t-o* tsh-iu* p-ing*": 1, "ts-iann* tsh-iu* p-ing*": 0, "ts-iann* p-ing*": 0
    })
}


def detect_language(recorder: AudioRecorder, timeout_seconds: float = 30.0) -> Language:
    language_keywords = {
        "中文": "zh-TW", "國語": "zh-TW",
        "English": "en", "英語": "en",
        "日本語": "ja", "t-ai* g-i*": "ta"
    }

    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        wav_file = recorder.record_speech(max_duration=5.0)
        if not wav_file:
            continue

        for lang_code, lang in LANGUAGE_MODELS.items():
            result = Recognizer(lang).recognize(wav_file)
            if result and result != "<{silent}>":
                for keyword, detected_code in language_keywords.items():
                    if keyword in result:
                        return LANGUAGE_MODELS[detected_code]

    raise TimeoutError("語言偵測逾時")
