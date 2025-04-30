from rpi.model import VisionTest, IResource
from main import main
from setting import *
import serial, logging

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
        self.logger.debug(f'Assume distance {TEST_START_DISTANCE}')
        return TEST_START_DISTANCE
    
    def oled_display(self):
        self.logger.debug('oled_display')
    
    def oled_clear(self):
        self.logger.debug('oled_clear')

    def oled_img(self, img):
        self.logger.debug('oled_img')
    
    def close(self):
        self.logger.debug('Close serial')
        self.ser.close()

    def get_test_resp(self, lang: int) -> int:
        self.logger.debug('get_test_resp, assuming resp = 0')
        return 0

    def get_lang_resp(self) -> int:
        self.logger.debug('get_lang_resp, assuming resp = 0')
        return 0


logging.basicConfig(level='DEBUG',
                    format=LOGGER_FORMAT,
                    filemode='w',
                    filename='.log')
res = ResourceDummy()
main(VisionTest(res))