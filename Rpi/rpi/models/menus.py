from typing import Callable
import logging
from setting import *
from PIL.Image import Image, new
from PIL import ImageDraw, ImageFont

class Menu: ...

class MenuElement:
    img: Image
    title: str
    call_back: Callable[[], int]

    def __init__(self, img: Image, call_back: Callable[[], int], title = None):
        self.img = img
        self.call_back = call_back
        self.title = title
    
    def indicate(self) -> Image:
        raise NotImplementedError()

class Menu:
    select_index: int
    item_list: list[MenuElement]
    item_height: int
    logger = logging.getLogger('Menu')

    def __init__(self, item_list: list[MenuElement], item_height: int):
        self.select_index = 0
        self.item_list = item_list
        self.item_height = item_height

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

    def select(self) -> int:
        """
        Call the call back func and return ns
        """
        
        return self.item_list[self.select_index].call_back()

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

class TextMenuElement(MenuElement):
    title: str

    def _str_cut(self, text: str) -> str:
        width = 0
        if text == None:
            return 'None'
        
        paste_text = ''

        for c in text:
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

    def __init__(self, text: str, call_back: Callable[[], int]):
        
        img = new('1', (128, MENU_TEXT_HEIGHT))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(**MENU_FONT)

        draw.rectangle((0, 0, 128, MENU_TEXT_HEIGHT), outline=0, fill=0)
        paste_text = self._str_cut(text)

        draw.text((2, 0), paste_text, font=font, fill=255)

        super().__init__(img, call_back, text)

    def indicate(self) -> Image:
        img = new('1', (128, MENU_TEXT_HEIGHT))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(**MENU_FONT)

        draw.rectangle((0, 0, 128, MENU_TEXT_HEIGHT), outline=0, fill=255)
        paste_text = self._str_cut(self.title)

        draw.text((2, 0), paste_text, font=font, fill=0)

        return img
    
    def __eq__(self, value: str):
        return self.title.__eq__(value)
    
class IconMenuElement(MenuElement):
    def __init__(self, img, call_back: Callable[[], int], title: str):
        super().__init__(img, call_back, title)

    def indicate(self) -> Image:
        return self.img


