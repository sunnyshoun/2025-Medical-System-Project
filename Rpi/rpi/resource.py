import RPi.GPIO as GPIO
from setting import *
from .models import IResource
from audio.recorder import AudioRecorder
from audio.recognizer import Recognizer, recognize_direct
from audio.language_detection import detect_language
from audio.player import audio_player
from audio.classes import Language
from bluetooth.device_manager import BluetoothScanner, set_device_volume
from bluetooth.classes import Device
import time, Adafruit_SSD1306, serial, logging
from PIL.Image import Image

class Resource(IResource):
    disp: Adafruit_SSD1306.SSD1306_128_64
    scanner: BluetoothScanner
    logger = logging.getLogger('Resource')
    logger.setLevel(LOGGER_LEVEL)

    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()

        self.scanner = BluetoothScanner()

        self.ser = serial.Serial(**RPI_SERIAL)

    def close(self):
        self.ser.close()

    def get_distance(self) -> float:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_SONIC_TRIGGER, GPIO.OUT)
        GPIO.setup(GPIO_SONIC_ECHO, GPIO.IN)

        # Ensure trigger is low
        GPIO.output(GPIO_SONIC_TRIGGER, False)
        time.sleep(0.05)

        # Send 10us pulse
        GPIO.output(GPIO_SONIC_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_SONIC_TRIGGER, False)

        # Wait for echo to go high
        start_time = time.time()
        while GPIO.input(GPIO_SONIC_ECHO) == 0 and time.time() - start_time < GPIO_SONIC_TIMEOUT:
            start = time.time()

        # Wait for echo to go low
        start_time = time.time()
        while GPIO.input(GPIO_SONIC_ECHO) == 1 and time.time() - start_time < GPIO_SONIC_TIMEOUT:
            end = time.time()

        GPIO.cleanup()

        try:
            time_elapsed = end - start
            distance = (time_elapsed * SONIC_SPEED) / 2
            return distance
        except:
            return -1.0  # error value if timing failed
    
    def oled_display(self):
        self.disp.display()
    
    def oled_clear(self):
        self.disp.clear()

    def oled_img(self, img: Image):
        self.disp.image(img.convert('1'))
    
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
        self.scanner.start()
        devices = self.scanner.list_devices()
        self.scanner.stop()
        return devices
    
    def connect_bt_device(self, device: Device):
        return super().connect_bt_device(device)
    
    def set_volume(self, volume: int):
        return set_device_volume(volume)
    
    def get_volume(self):
        return super().get_volume()
    
    def read_btn(self):
        raise NotImplementedError()
