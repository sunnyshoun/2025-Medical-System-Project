from rpi.model import IVisionTest
from main import TestingFlow
import serial, logging

class SerialDummy(serial.Serial):
    return_buf: list[bytes] = []
    logger = logging.getLogger('SerialDummy')

    def readline(self, size = -1):
        return self.return_buf.pop(0)
    
    def write(self, b: bytes):
        self.logger.debug(f'write: {b.decode()}')
        if b.startswith(b'm'):
            self.return_buf.append(b'ok')
            self.return_buf.append(b'done')

class VisionTestDummy(IVisionTest):
    ser = SerialDummy()

def main():
    TestingFlow.main(VisionTestDummy())