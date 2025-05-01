from setting import *
from audio.classes import Language
import serial
from PIL.Image import Image, new
from PIL import ImageDraw
from typing import Callable, List

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

class MenuElement:
    img: Image
    call_back: Callable[[], None]

    def __init__(self, img: Image, call_back: Callable[[], None]):
        self.img = img
        self.call_back = call_back

class Menu:
    select_index: int
    select_list: list[MenuElement]
    item_height: int
    items_visible: int

    def __init__(self, select_list: List[MenuElement]):
        self.select_index = 0
        self.select_list = select_list
        self.items_visible = SCREEN_HEIGHT // self.item_height

    def move_up(self):
        if self.select_index > 0:
            self.select_index -= 1

    def move_down(self):
        if self.select_index < len(self.select_list) - 1:
            self.select_index += 1

    def select(self):
        self.select_list[self.select_index].call_back()

    def list_img(self) -> Image:
        img = new('1', (SCREEN_WIDTH, SCREEN_HEIGHT))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), outline=0, fill=0)

        # 計算從哪個 index 開始畫，讓選中的項目在中間
        half_visible = self.items_visible // 2
        start_index = max(0, self.select_index - half_visible)
        end_index = min(len(self.select_list), start_index + self.items_visible)

        mid_pixel = (self.item_height - SCREEN_HEIGHT) // 2
        img.paste(self.select_list[self.select_index].img, (0, mid_pixel))

        offset_pixel = mid_pixel - self.item_height
        offset_index = self.select_index - 1
        while (offset_pixel > 0) and (offset_index >= 0):
            img.paste(self.select_list[offset_index].img, (0, offset_pixel))
            offset_pixel -= self.item_height
            offset_index -= 1
            
        offset_pixel = mid_pixel + self.item_height
        offset_index = self.select_index + 1
        while (offset_pixel < SCREEN_HEIGHT - self.item_height) and (offset_index < len(self.select_list)):
            img.paste(self.select_list[offset_index].img, (0, offset_pixel))
            offset_pixel -= self.item_height
            offset_index -= 1
            
        return img
