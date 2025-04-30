from rpi.model import VisionTest, IResource
from main import main
from setting import *
from test_model import ResourceDummy
import logging


logging.basicConfig(level='DEBUG',
                    format=LOGGER_FORMAT,
                    filemode='w',
                    filename='.log')
res = ResourceDummy()
main(VisionTest(res))