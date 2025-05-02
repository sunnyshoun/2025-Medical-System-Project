from .models import InterruptException, VisionTest
from audio.classes import Language
from setting import *
from data import vision
from data.draw import draw_circle_with_right_opening, paste_square_image_centered
from PIL.Image import Image, new
from PIL import ImageDraw, ImageFont
import logging, random

class Interrupt:
    """
    blocking, waiting, or something like that
    """

    logger = logging.getLogger('Interrupt')
    logger.setLevel(LOGGER_LEVEL)

    @classmethod
    def sorter(cls, ex: InterruptException):
        cls.logger.debug(f'Sorter got {ex.args}')

        test = ex.test
        ser = test.res.ser
        instruction = ex.args[0]

        dispatch = {
            INTERRUPT_INST_SHOW_RESULT: lambda: cls._handle_show_result(test, ex.args[1]),
            INTERRUPT_INST_START_MOV: lambda: cls._handle_start_mov(test, ex.args[1]),
            INTERRUPT_INST_SHOW_IMG: lambda: cls._handle_show_img(test),
            INTERRUPT_INST_USR_RESP: lambda: cls._handle_user_response(test),
        }

        handler = dispatch.get(instruction)
        if handler:
            handler()
        else:
            raise ValueError(f'Unexpected instruction code: {instruction}')

    @classmethod
    def _handle_show_result(cls, test: VisionTest, degree: float):
        cls.logger.debug('Show result')
        cls.show_result(test, degree)

    @classmethod
    def _handle_start_mov(cls, test: VisionTest, delta: float):
        target = test.cur_distance + (delta / 1000)
        cls.logger.info(f"Start moving {delta} mm to {round(target, 3)}")

        test.res.oled_clear()
        test.res.oled_display()

        msg = f'm{0 if delta > 0 else 1},{abs(delta)}\n'
        cls.logger.debug(f"sending: {msg.rstrip()}")
        test.res.ser.write(msg.encode())

        resp = test.res.ser.readline().decode().strip()
        if resp == 'ok':
            test.cur_distance = round(target, 3)
            cls.logger.debug(f"Start move got \"ok\"")
        else:
            raise ValueError(f'Unexpected response from start move: {resp}')

        cls.wait_mov(test)

    @classmethod
    def _handle_show_img(cls, test: VisionTest):
        thickness = vision.thickness[int(test.cur_degree * 10) - 1]
        img = draw_circle_with_right_opening(thickness=thickness)
        test.dir = random.randint(0, 3)
        cls.logger.debug(f"Dir: {test.dir}")
        result = paste_square_image_centered(img.rotate(test.dir * 90))
        cls.show_img(test, result)

    @classmethod
    def _handle_user_response(cls, test: VisionTest):
        test.got_resp = cls.test_resp(test)
        cls.logger.info(f'Got test response: {test.got_resp}')

    
    @classmethod
    def wait_mov(cls, test: VisionTest):
        resp = test.res.ser.readline().decode().strip()

        if resp == 'done':
            test.res.play_async(BEEP_FILE, 'all')
            cls.logger.info(f"Move done")
        else:
            raise ValueError(f'Unexpected response from wait move: {resp}')

    @classmethod
    def show_result(cls, test: VisionTest, degree: float) -> None:
        if abs(degree - INTERRUPT_RESULT_MIN) < 0.1:
            cls.logger.info('Test result: < 0.1')
            d = 0.0
        elif abs(degree - INTERRUPT_RESULT_MAX) < 0.1:
            cls.logger.info('Test result: >= 1.5')
            d = 1.6
        else:
            cls.logger.info(f'Test result: degree')
            d = degree

        image = new('1', (128, 64))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(**RESULT_FONT)

        draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
        draw.text((0, 0), RESULT_STRS[test.lang.lang_code], font=font, fill=255)
        draw.text((5, 22), f'{d:0.1f}', font=font, fill = 255)
        test.res.oled_img(image)
        test.res.oled_display()
        test.res.play_async(TEST_DONE_FILE, LANGUAGES[test.lang.lang_code])

    @classmethod
    def show_img(cls, test: VisionTest, img: Image) -> None:
        cls.logger.info(f'Show image, dir: {test.dir}')
        test.res.oled_img(img)
        test.res.oled_display()

    @classmethod
    def test_resp(cls, test: VisionTest) -> bool:
        while True:
            try:
                cls.logger.info(f'Waiting test resp')
                res = test.res.get_test_resp(test.lang)
                cls.logger.info(f'Got response: {res}')
                return  res == test.dir

            except ValueError as e:
                cls.logger.warning(e.args[0])
    
    @classmethod
    def lang_resp(cls, test: VisionTest) -> Language:
        while True:
            try:
                cls.logger.info(f'Waiting language resp')
                return test.res.get_lang_resp()

            except ValueError as e:
                cls.logger.warning(e.args[0])
