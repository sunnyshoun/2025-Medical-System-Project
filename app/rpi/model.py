from .setting import *
import serial

class VisionTest:
    cur_distance: float
    cur_degree: float
    max_degree = -1.0
    state = 0

    ser = serial.Serial(**RPI_SERIAL)

    moving = False
    got_resp: bool = None

class InterruptException(Exception):
    end: bool
    test: VisionTest
    def __init__(self, *args, end: bool, test: VisionTest = None):
        super().__init__(*args)
        self.end = end
        self.test = test