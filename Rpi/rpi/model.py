from setting import *
from audio.classes import Language
import serial, logging
from PIL.Image import Image, new
from PIL import ImageDraw, ImageFont
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
    title: str
    call_back: Callable[[], None]

    def __init__(self, img: Image, call_back: Callable[[], None]):
        self.img = img
        self.call_back = call_back
    
    def indicate(self) -> Image:
        raise NotImplementedError()

class TextMenuElement(MenuElement):
    HEIGHT: int = 20

    def str_cut(self) -> str:
        width = 0
        if self.title == None:
            return 'None'
        
        paste_text = ''

        for c in self.title:
            if 126 >= ord(c) >= 32:
                width += 1
            else:
                width += 2

            if width > MENU_MAX_TEXT_LEN:
                paste_text = paste_text[:-1] + '...'
                break
            else:
                paste_text += c

        return paste_text


    def __init__(self, text: str, call_back: Callable[[], None]):
        self.title = text
        
        img = new('1', (128, self.HEIGHT))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(**MENU_FONT)

        draw.rectangle((0, 0, 128, self.HEIGHT), outline=0, fill=0)
        paste_text = self.str_cut()

        draw.text((2, 0), paste_text, font=font, fill=255)

        super().__init__(img, call_back)

    def indicate(self) -> Image:
        img = new('1', (128, self.HEIGHT))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(**MENU_FONT)

        draw.rectangle((0, 0, 128, self.HEIGHT), outline=0, fill=255)
        paste_text = self.str_cut()

        draw.text((2, 0), paste_text, font=font, fill=0)

        return img

class Menu:
    select_index: int
    item_list: list[MenuElement]
    item_height: int
    items_visible: int
    logger = logging.getLogger('Menu')

    def __init__(self, item_list: List[MenuElement], item_height: int):
        self.select_index = 0
        self.item_list = item_list
        self.item_height = item_height
        self.items_visible = SCREEN_HEIGHT // self.item_height

    def move_up(self):
        if self.select_index > 0:
            self.select_index -= 1
        else:
            self.logger.info('Cannot move up')

    def move_down(self):
        if self.select_index < len(self.item_list) - 1:
            self.select_index += 1
        else:
            self.logger.info('Cannot move down')

    def select(self):
        self.item_list[self.select_index].call_back()

    def list_img(self) -> Image:
        img = new('1', (SCREEN_WIDTH, SCREEN_HEIGHT))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), outline=0, fill=0)
        
        mid_pixel = (SCREEN_HEIGHT - self.item_height) // 2
        img.paste(self.item_list[self.select_index].indicate(), (0, mid_pixel))
        self.logger.debug(f'Place selected item \"{self.item_list[self.select_index].title}\" at {mid_pixel}')

        offset_pixel = mid_pixel - self.item_height
        offset_index = self.select_index - 1
        while (offset_pixel > 0) and (offset_index >= 0):
            img.paste(self.item_list[offset_index].img, (0, offset_pixel))
            offset_pixel -= self.item_height
            offset_index -= 1
            
        offset_pixel = mid_pixel + self.item_height
        offset_index = self.select_index + 1
        while (offset_pixel < SCREEN_HEIGHT - self.item_height) and (offset_index < len(self.item_list)):
            img.paste(self.item_list[offset_index].img, (0, offset_pixel))
            offset_pixel += self.item_height
            offset_index += 1

        # indicator

        # 向上三角形（右上角）
        # 以右上角為基準，畫一個底為5，高為5的向上三角形
        if self.select_index > 0:
            up_triangle = [
                (SCREEN_WIDTH - 3, 0),          # 頂點（上方中央）
                (SCREEN_WIDTH - 6, 5),          # 左下角
                (SCREEN_WIDTH, 5)               # 右下角
            ]
            draw.polygon(up_triangle, fill=255)

        # 向下三角形（右下角）
        # 以右下角為基準，畫一個底為5，高為5的向下三角形
        if self.select_index < len(self.item_list) - 1:
            down_triangle = [
                (SCREEN_WIDTH - 3, SCREEN_HEIGHT),     # 頂點（下方中央）
                (SCREEN_WIDTH - 6, SCREEN_HEIGHT - 5), # 左上角
                (SCREEN_WIDTH, SCREEN_HEIGHT - 5)      # 右上角
            ]
            draw.polygon(down_triangle, fill=255)
            
        return img
