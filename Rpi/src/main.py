# Entry of the app running on Raspberry Pi 3B+

from rpi.menu import MainMenu
from rpi.models import VisionTest
from rpi.resource import Audio, Bluetooth, SttAPI
from hardwares import Motor, Oled, Sonic, Button
from rpi.tester import make_test
from settings import *
import logging, os, datetime


if __name__ == '__main__':
    logging.getLogger('Adafruit_I2C.Device.Bus.1.Address.0X3C').setLevel(logging.WARNING)

    stt = SttAPI()
    motor = Motor()
    sonic = Sonic()
    btn = Button()
    oled = Oled()
    audio = Audio()
    bluetooth = Bluetooth()

    def start_func():
        test = VisionTest(
            motor=motor,
            oled=oled,
            sonic=sonic,
            audio=audio,
            stt=stt
        )
        make_test(test)
        btn.read_btn()
        return MENU_STATE_ROOT
    
    menu = MainMenu(
        start_func,
        btn=btn,
        oled=oled,
        audio=audio,
        bluetooth=bluetooth
    )

    if not os.path.exists(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)

    log_name = datetime.datetime.strftime(datetime.datetime.now(), LOG_TIME_FORMAT)

    if SAVE_LOG:
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

    try:
        while True:
            menu.loop()
    except Exception:
        pass
