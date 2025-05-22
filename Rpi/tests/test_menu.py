from src.rpi.models import IButton
from settings import *
import os, logging
from src.rpi.menu import MainMenu
from tests.models import OledDummy, BluetoothDummy, ButtonDummy, AudioDummy
from pathlib import Path

os.chdir('./Rpi')

tests_dir = Path(__file__).parent
logging.basicConfig(level='DEBUG',
                    format=LOGGER_FORMAT,
                    filemode='w',
                    filename=tests_dir / '.log')

def start_func():
    logging.info('Called `start_func`')
    return MENU_STATE_ROOT


menu = MainMenu(
    start_func,
    btn=ButtonDummy(),
    oled=OledDummy(),
    audio=AudioDummy(),
    bluetooth=BluetoothDummy()
)

try:
    while True:
        menu.loop()
except IndexError:
    pass

