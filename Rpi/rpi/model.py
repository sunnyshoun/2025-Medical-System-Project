from setting import *
import serial, logging
from PIL.Image import Image

class IResource:
    ser: serial.Serial

    def __init__(self):
        logging.getLogger('IResource').error('Calling the interface method `__init__()`')
    
    def get_distance(self) -> float:
        logging.getLogger('IResource').error('Calling the interface method `get_distance()`')
    
    def oled_display(self):
        logging.getLogger('IResource').error('Calling the interface method `oled_display()`')
    
    def oled_clear(self):
        logging.getLogger('IResource').error('Calling the interface method `oled_clear()`')

    def oled_img(self, img: Image):
        logging.getLogger('IResource').error('Calling the interface method `oled_img()`')
    
    def close():
        logging.getLogger('IResource').error('Calling the interface method `close()`')

class VisionTest:
    cur_distance: float
    cur_degree: float
    max_degree: float
    state: int
    dir: int
    lang: int
    res: IResource

    moving: bool
    got_resp: bool

    def __init__(self, res: IResource):
        self.max_degree = -1.0
        self.state = 0

        self.moving = False
        self.got_resp = None
        self.dir = 0
        self.res = res

    def close(self ):
        self.res.close()

class InterruptException(Exception):
    end: bool
    test: VisionTest
    def __init__(self, *args, end: bool, test: VisionTest = None):
        super().__init__(*args)
        self.end = end
        self.test = test