from setting import *
from audio.classes import Language
import serial
from PIL.Image import Image

class IResource:
    ser: serial.Serial

    def __init__(self):
        raise NotImplementedError('Calling the interface method `__init__()`')
    
    def get_distance(self) -> float:
        raise NotImplementedError('Calling the interface method `get_distance()`')
    
    def oled_display(self):
        raise NotImplementedError('Calling the interface method `oled_display()`')
    
    def oled_clear(self):
        raise NotImplementedError('Calling the interface method `oled_clear()`')

    def oled_img(self, img: Image):
        raise NotImplementedError('Calling the interface method `oled_img()`')
    
    def close():
        raise NotImplementedError('Calling the interface method `close()`')

    def get_test_resp(self, lang: int) -> int:
        raise NotImplementedError('Calling the interface method `get_test_resp()`')

    def get_lang_resp(self) -> Language:
        raise NotImplementedError('Calling the interface method `get_lang_resp()`')
    
    def play_async(self, file_name: str, language: str, wait_time: int = 0):
        raise NotImplementedError('Calling the interface method `play_async`')

class VisionTest:
    cur_distance: float
    cur_degree: float
    max_degree: float
    state: int
    dir: int
    lang: Language
    res: IResource

    got_resp: bool

    def __init__(self, res: IResource):
        self.max_degree = -1.0
        self.state = 0

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