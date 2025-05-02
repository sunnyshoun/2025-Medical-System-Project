from rpi.models import Menu, TextMenuElement
from setting import *
import os, logging
from rpi.menu import MainMenu
from test_model import ResourceDummy

os.chdir('./Rpi')

logging.basicConfig(level='DEBUG', 
                    format=LOGGER_FORMAT,
                    filemode='w',
                    filename='.log')

def start_func():
    logging.info('Called `start_func`')

menu = MainMenu(start_func, ResourceDummy())

try:
    while True:
        menu.loop()
except IndexError:
    pass

