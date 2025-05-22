from settings import *
from .models import IAudio, IBluetooth, ISttAPI
from audio.recognizer import recognize_direct
from audio.language_detection import detect_language
from audio.player import audio_player
from audio.model import Language
from bluetooth.device_manager import BluetoothScanner, set_device_volume, connect_device
from bluetooth.model import Device
from config_manager import get_config_value
import logging

_LOGGER = logging.getLogger('Resource')
    
class Audio(IAudio):
    def play_async(self, file_name: str, language: str, wait_time: int = 0) -> None:
        return audio_player.play_async(file_name, language)
    
    def set_volume(self, volume: int) -> bool:
        return set_device_volume(volume)
    
    def get_volume(self) -> int:
        r = get_config_value('VOLUME')
        if type(r) is int:
            _LOGGER.debug(f'Get volume: {r}%')
            return r
        else:
            _LOGGER.warning('Cannot get volume')
            return -1
    
class Bluetooth(IBluetooth):
    scanner: BluetoothScanner

    def __init__(self) -> None:
        self.scanner = BluetoothScanner()

    def list_bt_device(self):
        devices = self.scanner.list_devices()
        return devices
    
    def connect_bt_device(self, device: Device):
        if connect_device(device):
            self.bt_device = device
            return True
        return False

class SttAPI(ISttAPI):
    def get_test_resp(self, lang: Language):
        while True:
            try:
                command = recognize_direct(lang)
                break
            except ValueError:
                audio_player.play_async(RECOGNITION_FAIL_FILE, LANGUAGES[lang.lang_code])
                _LOGGER.info("辨識失敗，請再說一次")
        return command
                    
    def get_lang_resp(self) -> Language:
        audio_player.play_async(ASK_LANG_FILE, 'all')
        while True:
            try:
                user_lang = detect_language()
                audio_player.stop()
                break
            except TimeoutError:
                audio_player.play_async(ASK_LANG_FILE, 'all')
                _LOGGER.info("未收到使用者語音，請再試一次")
        return user_lang
    