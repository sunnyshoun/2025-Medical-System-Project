from .model import InterruptException
from ..setting import *
from data.vision import get_thickness
from data.draw import draw_circle_with_right_opening, paste_square_image_centered
from PIL.Image import Image
import logging, random, time

class Interrupt:
    """
    blocking, waiting, or something like that
    """

    logger = logging.getLogger('Interrupt')

    def sorter(self, ex: InterruptException):
        self.logger.debug(f'Sorter got {ex.args}')

        test = ex.test
        ser = test.ser

        if ex.args[0] == INTERRUPT_INST_SHOW_RESULT:
            self.logger.debug('Show result')
            self.show_result(ex.args[1])

        elif ex.args[0] == INTERRUPT_INST_WAIT_MOV:
            self.logger.debug(f"Wait moving to distance: {test.cur_distance} m")

            resp = ser.readline().decode().strip()

            if resp == 'done':
                test.moving = False
            else:
                raise ValueError(f'Unexpected response: {resp}')

        elif ex.args[0] == INTERRUPT_INST_START_MOV:
            delta = ex.args[1]
            self.logger.debug(f"Start moving {delta} m to {test.cur_distance + (delta / 1000)}")

            msg = f'm{1 if delta > 0 else 0},{abs(delta)}\n'
            self.logger.debug(f"sending: {msg.rstrip()}")
            ser.write(msg.encode())

            resp = ser.readline().decode().strip()
            if resp == 'ok':
                test.moving = True
                test.cur_distance += delta / 1000
                self.logger.debug(f"cur_degree: {test.cur_degree}, cur_distance: {test.cur_distance}")
            else:
                raise ValueError(f'Unexpected response: {resp}')

        elif ex.args[0] == INTERRUPT_INST_SHOW_IMG:
            img = draw_circle_with_right_opening(thickness=get_thickness(test.cur_degree))
            result = paste_square_image_centered(img.rotate(random.choice([0, 90, 180, 270])))
            self.show_img(result)

        elif ex.args[0] == INTERRUPT_INST_USR_RESP:
            test.got_resp = self.usr_resp()

        else:
            raise ValueError(f'Unexpected instruction code: {ex.args[0]}')
        
    def show_result(self, degree: float) -> None:

        self.logger.warning('`show_result()` Not implemented')

    def show_img(self, img: Image) -> None:

        self.logger.warning('`show_img()` Not implemented')

    def usr_resp(self) -> bool:
        self.logger.warning('`usr_resp()` Not implemented')

        time.sleep(1)
        return True
