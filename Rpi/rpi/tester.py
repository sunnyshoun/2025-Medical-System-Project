from rpi.models import VisionTest, InterruptException
from rpi.interrupt import Interrupt
from settings import *
from data import vision
import logging, time

logger = logging.getLogger('TestingFlow')
logger.setLevel(LOGGER_LEVEL)

def setup(t: VisionTest):
    logger.info('Setup section')
    t.cur_degree = TEST_START_DEGREE
    t.cur_distance = -1.0
    
    while t.cur_distance < 0:
        t.cur_distance = t.res.get_distance()

    logger.info(f'Set cur_distance to {t.cur_distance}')

    logger.debug('Choose language')
    t.lang = Interrupt.lang_resp(t)
    while t.lang == None:
        t.lang = Interrupt.lang_resp(t)
        time.sleep(1)
        
    logger.info(f'Set language to: {t.lang.lang_code}')
    t.res.play_async(TEST_INTRO_FILE, LANGUAGES[t.lang.lang_code])

def loop(t: VisionTest):
    # === define ===
    _STATE_SET_UP = 0
    _STATE_SHOW_IMG = 1
    _STATE_INPUT = 2

    logger.info(f'--- Enter loop with state: {t.state} ---')
    logger.info(f'cur_degree: {t.cur_degree}, cur_distance: {t.cur_distance}')

    if t.state == _STATE_SET_UP:
        if 0.1 <= t.cur_degree and t.cur_degree <= 1.5:
            t.state = _STATE_SHOW_IMG
            t.got_resp = None

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

    elif t.state == _STATE_SHOW_IMG:
        target = vision.distance[int(t.cur_degree * 10) - 1]
        logger.debug(f'{abs(target - t.cur_distance)} m to target')
        if abs(target - t.cur_distance) < 0.001:
            # 不須移動
            t.state = _STATE_INPUT
            # 移動 target - t.cur_distance 公尺，換算毫米
            raise InterruptException(INTERRUPT_INST_SHOW_IMG,
                                    test=t,
                                    end=False)
        else:
            # 移動 target - t.cur_distance 公尺，換算毫米
            raise InterruptException(INTERRUPT_INST_START_MOV,
                                    int((target - t.cur_distance) * 1000),
                                    test=t,
                                    end=False)
    
    elif t.state == _STATE_INPUT:
        # 使用者是否看得清楚？
        if t.got_resp == None:
            raise InterruptException(INTERRUPT_INST_USR_RESP,
                                    test=t,
                                    end=False)
        else:
            t.state = _STATE_SET_UP
            if t.got_resp:
                t.max_degree = t.cur_degree
                t.cur_degree = round(t.cur_degree + 0.1, 1)
            elif t.max_degree < 0.0:
                t.cur_degree = round(t.cur_degree - 0.1, 1)
            else:
                raise InterruptException(INTERRUPT_INST_SHOW_RESULT,
                                        t.max_degree,
                                        test=t,
                                        end=True)

    else:
        raise ValueError(f'Unexpected state code: {t.state}')

    
def end(t: VisionTest):
    logger.info('End section')
    t.close()

def make_test(vision_test_obj: VisionTest):
    try:
        setup(vision_test_obj)

        while (True):
            try:
                loop(vision_test_obj)
                time.sleep(RPI_LOOP_INTERVAL)

            except InterruptException as ex:
                logger.debug(f'Interrupt: {ex.args}, end: {ex.end}')
                Interrupt.sorter(ex)
                if ex.end:
                    break
            
    except KeyboardInterrupt:
        logger.info('Catch KeyboardInterrupt')
        
    finally:
        end(vision_test_obj)

if __name__ == '__main__':

    raise RuntimeError('Should not be call as \"__main__\"')

    # from rpi.resource import Resource
    # logging.basicConfig(format=LOGGER_FORMAT)
    # main(VisionTest(Resource()), wait=TEST_SHOW_DURATION)