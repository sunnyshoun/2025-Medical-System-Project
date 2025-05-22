from settings import *
from serial import Serial
from rpi.models import IMotor
import logging

_SERIAL = Serial(**RPI_SERIAL)
_LOGGER = logging.getLogger('Motor')

class Motor(IMotor):
    def open_serial(self) -> None:
        if not _SERIAL.is_open:
            _LOGGER.debug('Open serial')
            _SERIAL.open()
    
    def close_serial(self) -> None:
        if _SERIAL.is_open:
            _LOGGER.debug('Close serial')
            _SERIAL.close()

    def write(self, msg: bytes) -> int | None:
        _LOGGER.debug(f'Write {msg}')
        return _SERIAL.write(msg)

    def readline(self) -> bytes:
        r = _SERIAL.readline()
        _LOGGER.debug(f'Read {r}')
        return r