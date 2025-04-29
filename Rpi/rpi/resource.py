import RPi.GPIO as GPIO
from setting import *
from model import IResource
import time, Adafruit_SSD1306, serial
from PIL.Image import Image

class Resource(IResource):
    disp: Adafruit_SSD1306.SSD1306_128_64

    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()

        self.ser = serial.Serial(**RPI_SERIAL)

    def close(self):
        self.ser.close()

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
        while GPIO.input(GPIO_SONIC_ECHO) == 0 and time.time() - start_time < GPIO_SONIC_TIMEOUT:
            start = time.time()

        # Wait for echo to go low
        start_time = time.time()
        while GPIO.input(GPIO_SONIC_ECHO) == 1 and time.time() - start_time < GPIO_SONIC_TIMEOUT:
            end = time.time()

        GPIO.cleanup()

        try:
            time_elapsed = end - start
            distance = (time_elapsed * 34300) / 2
            return distance
        except:
            return -1.0  # error value if timing failed
    
    def oled_display(self):
        self.disp.display()
    
    def oled_clear(self):
        self.disp.clear()

    def oled_img(self, img: Image):
        self.disp.image(img)
