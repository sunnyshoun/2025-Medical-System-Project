from .model import InterruptException
from .setting import *
from data.rpi.vision import get_distance, get_thickness
from data.rpi.draw import draw_circle_with_right_opening, paste_square_image_centered
import logging, random, time

class Interrupt:
    def sorter(ex: InterruptException):
        test = ex.test
        ser = test.ser

        if ex.args[0] == INTERRUPT_INST_SHOW_RESULT:
            logging.debug('Show result')
            logging.warning('Not implemented')

        elif ex.args[0] == INTERRUPT_INST_WAIT_MOV:
            resp = ser.readline().decode()
            if resp == 'done':
                test.moving = False
            else:
                raise ValueError(f'Unexpected response: {resp}')

        elif ex.args[0] == INTERRUPT_INST_START_MOV:
            delta_f = get_distance(test.cur_degree) - test.cur_distance
            delta = int(delta_f * 1000)
            msg = f'm{1 if delta > 0 else 0},{abs(delta)}\n'
            ser.write(msg.encode())
            time.sleep(0.5)
            resp = ser.readline().decode()
            if resp == 'ok':
                test.moving = True
                test.cur_distance += delta 
                logging.debug(f"cur_degree: {test.cur_degree}, cur_distance: {test.cur_distance}, sending: {msg.rstrip()}")
            else:
                raise ValueError(f'Unexpected response: {resp}')

        elif ex.args[0] == INTERRUPT_INST_SHOW_IMG:
            img = draw_circle_with_right_opening(thickness=get_thickness(test.cur_degree))
            result = paste_square_image_centered(img.rotate(random.choice([0, 90, 180, 270])))
            logging.debug('Generate image')
            logging.warning('Not implemented')

        elif ex.args[0] == INTERRUPT_INST_GET_RESP:
            time.sleep(1)

        else:
            raise ValueError(f'Unexpected instruction code: {ex.args[0]}')
    
    def usr_resp():
        raise NotImplementedError()
