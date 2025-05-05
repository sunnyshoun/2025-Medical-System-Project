# Entry of the app running on Raspberry Pi 3B+

from rpi.menu import MainMenu
from rpi.models import VisionTest, IResource
from rpi.tester import make_test
from setting import *
import logging, os, datetime

def start_func(res: IResource):
    test = VisionTest(res)
    make_test(test)
    res.read_btn()

if __name__ == '__main__':
    from rpi.resource import Resource
    res = Resource()

    if not os.path.exists(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)

    log_name = datetime.datetime.strftime(datetime.datetime.now(), LOG_TIME_FORMAT)

    logging.basicConfig(
        level=LOGGER_LEVEL, 
        format=LOGGER_FORMAT,
        filemode='w',
        filename=f'{LOG_FOLDER}{log_name}.log'
        )

    menu = MainMenu(start_func, res)

    try:
        while True:
            menu.loop()
    except IndexError:
        pass
