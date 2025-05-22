import RPi.GPIO as GPIO
from settings import *
import time

def read_btn():
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
                    return pin
            time.sleep(0.05)
    finally:
        GPIO.cleanup()
        