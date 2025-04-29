from recorder import AudioRecorder
from recognizer import StreamingRecognizer
from language_detection import detect_language

def main() -> None:
    try:
        # 第一步：檢測語言
        user_lang = detect_language(timeout_seconds=30.0)
        if user_lang is None:
            print("未檢測到語言。退出。")
            return
        print(f"使用者語言：{user_lang.api_lang}")

        recorder = AudioRecorder()
        recorder.start()
        recognizer = StreamingRecognizer(recorder, language=user_lang.api_lang)
        result = recognizer.recognize_once()
        print(f"語音內容：{result}")

    except Exception as e:
        print(f"主程式錯誤：{e}")
    finally:
        recorder.stop()

if __name__ == "__main__":
    main()