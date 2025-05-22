from settings import *
import RPi.GPIO as GPIO
from rpi.models import IButton
import time, logging

_LOGGER = logging.getLogger('Button')

class Button(IButton):
    def read_btn(self) -> int:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        btn_pins = [BTN_UP, BTN_CONFIRM, BTN_DOWN]

        for pin in btn_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        try:
            while True:
                for pin in btn_pins:
                    if not GPIO.input(pin):
                        while not GPIO.input(pin):
                            time.sleep(0.05)
                        _LOGGER.debug(f'Read btn: {pin}')
                        return pin
                time.sleep(0.05)
        finally:
            GPIO.cleanup()
        