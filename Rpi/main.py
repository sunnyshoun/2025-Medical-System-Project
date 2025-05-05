# Entry of the app running on Raspberry Pi 3B+

from rpi.menu import MainMenu
from rpi.models import VisionTest, IResource
from rpi.tester import make_test
from setting import *
import logging, os, datetime


if __name__ == '__main__':
    from rpi.resource import Resource
    res = Resource()
    logging.getLogger('Adafruit_I2C.Device.Bus.1.Address.0X3C').setLevel(logging.WARNING)
    
    def start_func():
        test = VisionTest(res)
        make_test(test)
        res.read_btn()

    if not os.path.exists(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)

    log_name = datetime.datetime.strftime(datetime.datetime.now(), LOG_TIME_FORMAT)

    if SVAE_LOG:
        logging.basicConfig(
            level=LOGGER_LEVEL, 
            format=LOGGER_FORMAT,
            filemode='w',
            filename=f'{LOG_FOLDER}{log_name}.log'
            )
    else:
        logging.basicConfig(
            level=LOGGER_LEVEL, 
            format=LOGGER_FORMAT
            )

    menu = MainMenu(start_func, res)

    try:
        while True:
            menu.loop()
    except IndexError:
        pass
