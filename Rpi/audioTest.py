from audio.recorder import AudioRecorder
from audio.recognizer import Recognizer, recognize_direct
from audio.language_detection import detect_language


def main():
    recorder = AudioRecorder(device_index=11)
    try:
        while True:
            try:
                user_lang = detect_language(recorder)
                break
            except TimeoutError:
                print("未收到使用者語音，請再試一次")

        print(f"偵測語言：{user_lang.api_lang}")
        
        recognizer = Recognizer(user_lang)
        while True:
            try:
                command = recognize_direct(recorder, recognizer)
                print(f"辨識指令：{command}")
            except ValueError:
                print("辨識失敗，請再說一次")

    except Exception as e:
        print(f"主程式錯誤：{e}")
    finally:
        recorder.stop()


if __name__ == "__main__":
    main()
