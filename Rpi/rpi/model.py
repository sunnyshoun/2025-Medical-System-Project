from setting import *
from audio.classes import Language
import serial
from PIL.Image import Image, new
from PIL import ImageDraw
from typing import Callable

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

class MainMenu:
    bluetooth: object
    res: IResource
    state: int
    select: int
    select_list: list[object]

    def __init__(self):
        
        raise NotImplementedError()

    def show_list():
        img = new('1', (128, 64))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 128, 64), outline=0, fill=0)

        raise NotImplementedError()

class Widget(Image):
    call_back: Callable[[None], None]

    def open(self, call_back: Callable[[None], None]):
        self.call_back = call_back
        raise NotImplementedError()

    def selected(self):
        self.call_back()