from .model import VisionTest, InterruptException
from .interrupt import Interrupt
from .setting import *
from data.rpi.vision import get_distance
import logging, time

def setup(t: VisionTest):
    t.cur_degree = TEST_START_DEGREE
    t.cur_distance = TEST_START_DISTANCE
    logging.debug('VisionTest initialized')

def loop(t: VisionTest):
    _STATE_PRE_INPUT = 0
    _STATE_MOVE = 1
    # _STATE_SHOW_IMG = 2
    _STATE_INPUT = 3
    # _STATE_POST_INPUT = 4

    if t.state == _STATE_PRE_INPUT:
        if 0.1 <= t.cur_degree and t.cur_degree <= 1.5:
            t.state = _STATE_MOVE

        else:
            if t.max_degree < 0:
                # 結束測試，度數小於最低值
                raise InterruptException(INTERRUPT_INST_SHOW_RESULT,
                                         INTERRUPT_RESULT_MIN,
                                         test=t,
                                         end=True)
            else:
                # 結束測試，度數大於最高值
                raise InterruptException(INTERRUPT_INST_SHOW_RESULT,
                                         INTERRUPT_RESULT_MAX,
                                         test=t,
                                         end=True)

    elif t.state == _STATE_MOVE:
        # 移動至對應位置
        if t.moving:
            raise InterruptException(INTERRUPT_INST_WAIT_MOV,
                                     test=t,
                                     end=False)
        else:
            target = get_distance(t.cur_degree)
            if target - t.cur_distance < 0.001:
                # 不須移動
                t.state = _STATE_INPUT
            else:
                t.cur_distance = target
                raise InterruptException(INTERRUPT_INST_START_MOV,
                                         target - t.cur_distance,
                                         test=t,
                                         end=False)
    
    elif t.state == _STATE_INPUT:
        # 使用者是否看得清楚？
        if t.got_resp == None:
            raise InterruptException(INTERRUPT_INST_GET_RESP,
                                     test=t,
                                     end=False)
        else:
            if t.got_resp:
                t.max_degree = t.cur_degree
                t.cur_degree += 1
            elif t.max_degree < 0.0:
                t.cur_degree -= 1
            else:
                raise InterruptException(INTERRUPT_INST_SHOW_RESULT,
                                         t.max_degree,
                                         test=t,
                                         end=True)

    else:
        raise ValueError(f'Unexpected state code: {t.state}')

def end(t: VisionTest):
    logging.debug('End section')
    t.ser.close()

def main():
    TEST = VisionTest()
    try:
        setup(TEST)

        while (True):
            try:
                loop(TEST)

            except InterruptException as ex:
                logging.debug(f'Interrupt: {ex.args}, end: {ex.end}')
                Interrupt.sorter(ex)
                if ex.end:
                    break
            
            time.sleep(RPI_LOOP_INTERVAL)
            
    except KeyboardInterrupt:
        logging.debug('Catch KeyboardInterrupt')
        
    finally:
        end(TEST)

if __name__ == '__main__':
    main()