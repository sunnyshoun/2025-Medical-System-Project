from rpi.models import VisionTest
from rpi.tester import main
from setting import *
from test_model import ResourceDummy
import logging, os


logging.basicConfig(level='DEBUG',
                    format=LOGGER_FORMAT,
                    filemode='w',
                    filename='.log')
res = ResourceDummy()
os.chdir('./Rpi')
main(VisionTest(res))