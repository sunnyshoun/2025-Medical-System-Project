from serial import Serial
from settings import *

_SERIAL = Serial(**RPI_SERIAL)

def close_serial():
    _SERIAL.close()