import logging, hashlib
from audio.model import Language
from PIL.Image import Image
from pathlib import Path
from bluetooth.base import Device
from src.rpi.models import IMotor, IOled, ISonic, IAudio, IBluetooth, ISttAPI, IButton
from tb import *

class MotorDummy(IMotor):
    return_buf: list[bytes] = []
    logger = logging.getLogger('SerialDummy')

    def readline(self):
        return self.return_buf.pop(0)
    
    def write(self, msg: bytes):
        self.logger.debug(f'write: {msg.decode().strip()}')
        if msg.startswith(b'm'):
            self.return_buf.append(b'ok')
            self.return_buf.append(b'done')
            
    def close_serial(self):
        self.logger.debug('Close serial')

class OledDummy(IOled):
    logger = logging.getLogger('OledDummy')
    def display(self) -> None:
        self.logger.debug('Calling `display()`')
    def clear(self) -> None:
        self.logger.debug('Calling `clear()`')
    def set_img(self, img: Image) -> None:
        tmp_dir = Path(__file__).parent / '.tmp'
        tmp_dir.mkdir(exist_ok=True)

        img_bytes = img.tobytes()
        img_hash = hashlib.sha256(img_bytes).hexdigest()
        file_path = tmp_dir / f'{img_hash}.png'

        self.logger.debug(f'set_img save image to {file_path}')
        img.save(file_path)

class SonicDummy(ISonic):
    logger = logging.getLogger('SonicDummy')
    def get_distance(self) -> float:
        self.logger.debug('Calling `get_distance()`, return 0')
        return 0
    

class AudioDummy(IAudio):
    logger = logging.getLogger('AudioDummy')
    def play_async(self, file_name: str, language: str, wait_time: int = 0) -> None:
        self.logger.debug(f'Playing: \"{file_name}\", lang: \"{language}\"')
    def set_volume(self, volume: int) -> bool:
        self.logger.info(f'Set volume to {volume}%')
        return True
    def get_volume(self) -> int:
        self.logger.debug('Calling `get_volume`, return 50%')
        return 50

class BluetoothDummy(IBluetooth):
    logger = logging.getLogger('BluetoothDummy')
    def list_bt_device(self) -> list[Device]:
        d = [
            Device('asdasd', 'FF:FF:FF:FF:FF:F0'),
            Device('asdasdasdasdasd', 'FF:FF:FF:FF:FF:F1'),
            Device('ㄚㄚㄚㄚㄚㄚ', 'FF:FF:FF:FF:FF:F2'),
            Device('ㄚ1ㄚㄚㄚㄚㄚㄚ1', 'FF:FF:FF:FF:FF:F3')
        ]
        self.logger.debug(f'Using testing bt devices: {", ".join([t.device_name for t in [*d]])}')

        return d
    def connect_bt_device(self, device: Device) -> bool:
        self.logger.info(f'connect to {device.device_name}')
        if device.device_name == 'default':
            self.bt_device = None
            return False
        else:
            self.bt_device = device
            return True

class SttAPIDummy(ISttAPI):
    logger = logging.getLogger('SttAPIDummy')
    def get_test_resp(self, lang: Language) -> int:
        self.logger.debug('get_test_resp, assuming resp = 0')
        return 0
    def get_lang_resp(self) -> Language:
        
        self.logger.debug('get_lang_resp, assuming resp = 0')
        return Language(0, "STT for course", {"上": 1, "上面": 1, "下": 3, "下面": 3, "左": 2, "左邊": 2, "右": 0, "右邊": 0, "yo": 0})
    
class ButtonDummy(IButton):
    i = 0
    def read_btn(self):
        btn = RES_READ_BTN_YIELDING[self.i]
        self.i += 1
        return btn

