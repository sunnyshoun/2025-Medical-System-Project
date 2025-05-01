import serial, logging, hashlib
from rpi.model import IResource
from audio.classes import Language
from PIL.Image import Image
from pathlib import Path

class SerialDummy(serial.Serial):
    return_buf: list[bytes] = []
    logger = logging.getLogger('SerialDummy')

    def readline(self, size = -1):
        return self.return_buf.pop(0)
    
    def write(self, b: bytes):
        self.logger.debug(f'write: {b.decode().strip()}')
        if b.startswith(b'm'):
            self.return_buf.append(b'ok')
            self.return_buf.append(b'done')



class ResourceDummy(IResource):
    def __init__(self):
        self.ser = SerialDummy()
        self.logger = logging.getLogger('ResourceDummy')
    
    def get_distance(self) -> float:
        self.logger.debug(f'Assume distance {0}')
        return 0
    
    def oled_display(self):
        self.logger.debug('oled_display')
    
    def oled_clear(self):
        self.logger.debug('oled_clear')

    def oled_img(self, img: Image):
        cache_dir = Path(__file__).parent / '.cache'
        cache_dir.mkdir(exist_ok=True)

        img_bytes = img.tobytes()
        img_hash = hashlib.sha256(img_bytes).hexdigest()
        file_path = cache_dir / f'{img_hash}.png'

        self.logger.debug(f'oled_img save img to {file_path}')
        img.save(file_path)
    
    def close(self):
        self.logger.debug('Close serial')
        self.ser.close()

    def get_test_resp(self, lang: int) -> int:
        self.logger.debug('get_test_resp, assuming resp = 0')
        return 0

    def get_lang_resp(self) -> Language:
        self.logger.debug('get_lang_resp, assuming resp = 0')
        return Language(0, "STT for course", {"上": 1, "上面": 1, "下": 3, "下面": 3, "左": 2, "左邊": 2, "右": 0, "右邊": 0, "yo": 0})
    
    def play_async(self, file_name: str, language: str, wait_time: int = 0):
        self.logger.debug(f'Playing: \"{file_name}\", lang: \"{language}\"')