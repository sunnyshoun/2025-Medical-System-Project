import subprocess
import os
from config_manager import load_config

class AudioPlayer:
    def __init__(self):
        config = load_config()
        self.headphone_mac = config.get('HEADPHONE_DEVICE_MAC')
        self.volume = config.get('VOLUME')
        
        if not self.headphone_mac or not self.volume:
            raise ValueError("HEADPHONE_DEVICE_MAC or VOLUME not found in config")

        subprocess.run(["pactl", "set-sink-volume", f"bluez_output.{self.headphone_mac}.1", f"{self.volume}"], check=True)
        self.base_folder = os.path.join(os.path.dirname(__file__), "audioFiles")
        self.process = None

    def play_async(self, file_name: str, language: str, wait_time: int = 0):
        """
        非同步播放指定語言資料夾下的音訊檔案。
        :param file_name: 音訊檔名 (e.g. hello.wav)
        :param language: 語言資料夾名稱 (e.g. en, zh)
        """
        self.stop()  # 如果之前有播放，先終止

        audio_path = os.path.join(self.base_folder, language, file_name)

        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"音訊檔不存在: {audio_path}")

        self.process = subprocess.Popen(["aplay", audio_path])

    def wait_play_done(self):
        """等待目前音訊播放完成。"""
        if self.process:
            self.process.wait()

    def stop(self):
        """中斷目前的播放（如果有的話）。"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
            self.process = None

audio_player = AudioPlayer()