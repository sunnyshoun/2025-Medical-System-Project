from PIL.Image import Image
from rpi.models import IOled
import Adafruit_SSD1306, logging

_DISP = Adafruit_SSD1306.SSD1306_128_64(rst=None)
_LOGGER = logging.getLogger('Oled')

class Oled(IOled):
    def display(self) -> None:
        _LOGGER.debug('display')
        _DISP.display()

    def clear(self) -> None:
        _LOGGER.debug('clear')
        _DISP.clear()

    def set_img(self, img: Image) -> None:
        _LOGGER.debug('set_img')
        _DISP.image(img.convert('1'))
