from setting import *
import serial


class IVisionTest:
    cur_distance: float
    cur_degree: float
    max_degree: float
    state: int
    dir: int
    lang: int

    moving: bool
    got_resp: bool

    def __init__(self):
        self.max_degree = -1.0
        self.state = 0

        self.moving = False
        self.got_resp = None
        self.dir = 0

class VisionTest(IVisionTest):

    ser: serial.Serial

    def __init__(self):
        super().__init__()
        self.ser = serial.Serial(**RPI_SERIAL)

class InterruptException(Exception):
    end: bool
    test: VisionTest
    def __init__(self, *args, end: bool, test: VisionTest = None):
        super().__init__(*args)
        self.end = end
        self.test = test