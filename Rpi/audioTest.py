from audio.recorder import AudioRecorder
from audio.recognizer import Recognizer, recognize_direct
from audio.language_detection import detect_language

def main() -> None:
    try:
        # 第一步：檢測語言
        recorder = AudioRecorder(device_index=11)
        while True:
            try:
                user_lang = detect_language(recorder, timeout_seconds=30.0)
                break
            except TimeoutError:
                print("使用者沒有回應")
                
        print(f"使用者語言：{user_lang.api_lang}")

        recognizer = Recognizer(user_lang)
        while True:
            try:
                print(recognize_direct(recorder, recognizer))
            except ValueError:
                print("使用者說錯話")

    except Exception as e:
        print(f"主程式錯誤：{e}")
    finally:
        recorder.stop()

if __name__ == "__main__":
    main()