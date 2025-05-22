from PIL.Image import Image
import Adafruit_SSD1306

_DISP = Adafruit_SSD1306.SSD1306_128_64(rst=None)
    
def oled_display():
    _DISP.display()

def oled_clear():
    _DISP.clear()

def oled_img(img: Image):
    _DISP.image(img.convert('1'))