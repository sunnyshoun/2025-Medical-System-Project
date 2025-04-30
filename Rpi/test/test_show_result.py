from rpi.interrupt import Interrupt
from rpi.resource import Resource
from rpi.model import VisionTest


class OLEDResource(Resource):
    def __init__(self):
        super().__init__()
        
    def get_lang_resp(self):
        pass

    def get_test_resp(self, lang):
        pass

test = VisionTest(OLEDResource())
test.lang = 3

Interrupt.show_result(test, 1.0)
input('Enter to leave...')