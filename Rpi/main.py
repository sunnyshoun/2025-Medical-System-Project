from rpi.model import VisionTest, InterruptException
from rpi.interrupt import Interrupt
from Rpi.setting import *
from data.vision import get_distance
import logging, time, argparse

class TestingFlow:

    logger = logging.getLogger('TestingFlow')

    def setup(self, t: VisionTest):
        self.logger.debug('Setup section')
        t.cur_degree = TEST_START_DEGREE
        t.cur_distance = TEST_START_DISTANCE
        self.logger.debug('VisionTest initialized')

    def loop(self, t: VisionTest):
        # === define ===
        _STATE_SET_UP = 0
        _STATE_SHOW_IMG = 1
        _STATE_INPUT = 2

        self.logger.debug(f'--- Enter loop with state: {t.state} ---')
        self.logger.debug(f'cur_degree: {t.cur_degree}, cur_distance: {t.cur_distance}')

        if t.state == _STATE_SET_UP:
            if 0.1 <= t.cur_degree and t.cur_degree <= 1.5:
                t.state = _STATE_SHOW_IMG
                t.got_resp = None
                t.moving = False

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
            # 移動至對應位置
            if t.moving:
                raise InterruptException(INTERRUPT_INST_WAIT_MOV,
                                        test=t,
                                        end=False)
            else:
                target = get_distance(t.cur_degree)
                if abs(target - t.cur_distance) < 0.001:
                    # 不須移動
                    t.state = _STATE_INPUT
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
                    t.cur_degree += 0.1
                elif t.max_degree < 0.0:
                    t.cur_degree -= 0.1
                else:
                    raise InterruptException(INTERRUPT_INST_SHOW_RESULT,
                                            t.max_degree,
                                            test=t,
                                            end=True)

        else:
            raise ValueError(f'Unexpected state code: {t.state}')

    def end(self, t: VisionTest):
        self.logger.debug('End section')
        t.ser.close()

    def main(self, vision_test_obj: VisionTest):
        try:
            self.setup(vision_test_obj)

            while (True):
                try:
                    self.loop(vision_test_obj)
                    time.sleep(RPI_LOOP_INTERVAL)

                except InterruptException as ex:
                    self.logger.debug(f'Interrupt: {ex.args}, end: {ex.end}')
                    Interrupt.sorter(ex)
                    if ex.end:
                        break
                
        except KeyboardInterrupt:
            self.logger.debug('Catch KeyboardInterrupt')
            
        finally:
            self.end(vision_test_obj)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument( '-log',
                        '--loglevel',
                        default='warning',
                        help='Provide logging level. Example --loglevel debug, default=warning' )

    args = parser.parse_args()

    logging.basicConfig(format="%(name)-11s:%(levelname)-4s: %(message)s",
                        level=args.loglevel.upper())

    TestingFlow.main(VisionTest())