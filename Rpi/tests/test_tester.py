from src.rpi.models import VisionTest
from src.rpi.tester import make_test
from settings import *
from tests.models import MotorDummy, OledDummy, SonicDummy, AudioDummy, SttAPIDummy
import logging, os
from pathlib import Path

tests_dir = Path(__file__).parent
logging.basicConfig(level='DEBUG',
                    format=LOGGER_FORMAT,
                    filemode='w',
                    filename=tests_dir / '.log')

os.chdir('./Rpi')
tester = VisionTest(
    motor=MotorDummy(),
    oled=OledDummy(),
    sonic=SonicDummy(),
    audio=AudioDummy(),
    stt=SttAPIDummy()
)

make_test(tester)