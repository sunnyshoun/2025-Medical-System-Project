from .model import InterruptException, VisionTest
from setting import *
from data.vision import get_thickness
from data.draw import draw_circle_with_right_opening, paste_square_image_centered
from PIL.Image import Image
import logging, random

class Interrupt:
    """
    blocking, waiting, or something like that
    """

    logger = logging.getLogger('Interrupt')

    @classmethod
    def sorter(cls, ex: InterruptException):
        cls.logger.debug(f'Sorter got {ex.args}')

        test = ex.test
        ser = test.ser

        if ex.args[0] == INTERRUPT_INST_SHOW_RESULT:
            cls.logger.debug('Show result')
            cls.show_result(ex.args[1])

        elif ex.args[0] == INTERRUPT_INST_WAIT_MOV:
            cls.wait_mov()

        elif ex.args[0] == INTERRUPT_INST_START_MOV:
            delta = ex.args[1]
            cls.logger.info(f"Start moving {delta} m to {test.cur_distance + (delta / 1000)}")

            msg = f'm{1 if delta > 0 else 0},{abs(delta)}\n'
            cls.logger.debug(f"sending: {msg.rstrip()}")
            ser.write(msg.encode())

            resp = ser.readline().decode().strip()
            if resp == 'ok':
                test.moving = True
                test.cur_distance += delta / 1000
                cls.logger.debug(f"cur_degree: {test.cur_degree}, cur_distance: {test.cur_distance}")
            else:
                raise ValueError(f'Unexpected response from start move: {resp}')
            
            cls.wait_mov(test)

        elif ex.args[0] == INTERRUPT_INST_SHOW_IMG:
            img = draw_circle_with_right_opening(thickness=get_thickness(test.cur_degree))
            test.dir = random.randint(0, 3)

            result = paste_square_image_centered(img.rotate(test.dir * 90))
            cls.show_img(result)

        elif ex.args[0] == INTERRUPT_INST_USR_RESP:
            test.got_resp = cls.test_resp()

        else:
            raise ValueError(f'Unexpected instruction code: {ex.args[0]}')
    
    @classmethod
    def wait_mov(cls, test: VisionTest):
        cls.logger.debug(f"Wait moving to {test.cur_distance} m")

        resp = test.ser.readline().decode().strip()

        if resp == 'done':
            test.moving = False
        else:
            raise ValueError(f'Unexpected response from wait move: {resp}')

    @classmethod
    def show_result(cls, degree: float) -> None:

        cls.logger.warning('`show_result()` Not implemented')

    @classmethod
    def show_img(cls, img: Image) -> None:

        cls.logger.warning('`show_img()` Not implemented')

    @classmethod
    def test_resp(cls) -> bool:
        cls.logger.warning('`usr_resp()` Not implemented')

        return True
    
    @classmethod
    def lang_resp(cls) -> int:
        cls.logger.warning('`lang_resp()` Not implemented')

        return 0
