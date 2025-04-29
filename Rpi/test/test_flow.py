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
    
    def get_distance(self) -> float:
        logging.getLogger('ResourceDummy').debug(f'Assume distance {TEST_START_DISTANCE}')
        return TEST_START_DISTANCE
    
    def oled_display(self):
        logging.getLogger('ResourceDummy').debug('oled_display')
    
    def oled_clear(self):
        logging.getLogger('ResourceDummy').debug('oled_clear')

    def oled_img(self, img):
        logging.getLogger('ResourceDummy').debug('oled_img')
    
    def close(self):
        logging.getLogger('ResourceDummy').debug('Close serial')
        self.ser.close()


logging.basicConfig(level='DEBUG',
                    format=LOGGER_FORMAT,
                    filemode='w',
                    filename='.log')
res = ResourceDummy()
main(VisionTest(res))