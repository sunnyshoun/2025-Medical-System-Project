import RPi.GPIO as GPIO
from settings import *
from .models import IResource
from audio.recorder import AudioRecorder
from audio.recognizer import Recognizer, recognize_direct
from audio.language_detection import detect_language
from audio.player import audio_player
from audio.model import Language
from bluetooth.device_manager import BluetoothScanner, set_device_volume, connect_device
from bluetooth.base import Device
import time, Adafruit_SSD1306, serial, logging
from PIL.Image import Image

class Resource(IResource):
    disp: Adafruit_SSD1306.SSD1306_128_64
    scanner: BluetoothScanner
    ser: serial.Serial
    bt_device: Device
    logger = logging.getLogger('Resource')
    logger.setLevel(LOGGER_LEVEL)

    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()

        self.scanner = BluetoothScanner()

        self.ser = serial.Serial(**RPI_SERIAL)
        self.bt_device = None
    
    def get_test_resp(self, lang: Language):
        recorder = AudioRecorder()
        recognizer = Recognizer(lang)
        try:
            while True:
                try:
                    command = recognize_direct(recorder, recognizer)
                    break
                except ValueError:
                    audio_player.play_async(RECOGNITION_FAIL_FILE, LANGUAGES[lang.lang_code])
                    self.logger.info("辨識失敗，請再說一次")
        finally:
            recorder.stop()
        return command
                    
    def get_lang_resp(self) -> Language:
        recorder = AudioRecorder()
        audio_player.play_async(ASK_LANG_FILE, 'all')
        try:
            while True:
                try:
                    user_lang = detect_language(recorder)
                    audio_player.stop()
                    break
                except TimeoutError:
                    audio_player.play_async(ASK_LANG_FILE, 'all')
                    self.logger.info("未收到使用者語音，請再試一次")
        finally:
            recorder.stop()
        return user_lang
    
    def play_async(self, file_name: str, language: str, wait_time: int = 0):
        return audio_player.play_async(file_name, language, wait_time)
    
    def list_bt_device(self):
        devices = self.scanner.list_devices()
        return devices
    
    def connect_bt_device(self, device: Device):
        if connect_device(device):
            self.bt_device = device
            return True
        return False
