from settings import *
from rpi.models import ISonic
import RPi.GPIO as GPIO
import time, logging

_LOGGER = logging.getLogger('Sonic')

class Sonic(ISonic):
    def get_distance(self) -> float:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_SONIC_TRIGGER, GPIO.OUT)
        GPIO.setup(GPIO_SONIC_ECHO, GPIO.IN)

        # Ensure trigger is low
        GPIO.output(GPIO_SONIC_TRIGGER, False)
        time.sleep(0.05)

        # Send 10us pulse
        GPIO.output(GPIO_SONIC_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_SONIC_TRIGGER, False)

        # Wait for echo to go high
        start_time = time.time()
        start = start_time
        while GPIO.input(GPIO_SONIC_ECHO) == 0 and time.time() - start_time < GPIO_SONIC_TIMEOUT:
            start = time.time()

        # Wait for echo to go low
        start_time = time.time()
        end = start_time
        while GPIO.input(GPIO_SONIC_ECHO) == 1 and time.time() - start_time < GPIO_SONIC_TIMEOUT:
            end = time.time()

        GPIO.cleanup()

        try:
            time_elapsed = end - start
            distance = (time_elapsed * SONIC_SPEED) / 2
            _LOGGER.debug(f'Distance: {distance}, start: {start}, end: {end}')
            return distance
        except:
            _LOGGER.warning('Timing failed, returned -1.0')
            return -1.0  # error value if timing failed
