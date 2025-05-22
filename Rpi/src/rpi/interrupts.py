from .models import InterruptException, VisionTest
from audio.classes import Language
from audio.player import audio_player
from settings import *
from ..data import vision
from ..data.draw import draw_circle_with_right_opening, paste_square_image_centered
from PIL.Image import Image, new
from PIL import ImageDraw, ImageFont
import logging, random

_LOGGER = logging.getLogger('Interrupt')

def sorter(ex: InterruptException):
    _LOGGER.debug(f'Sorter got {ex.args}')

    test = ex.test
    instruction = ex.args[0]

    dispatch = {
        INTERRUPT_INST_SHOW_RESULT: lambda: _handle_show_result(test, ex.args[1]),
        INTERRUPT_INST_START_MOV: lambda: _handle_start_mov(test, ex.args[1]),
        INTERRUPT_INST_SHOW_IMG: lambda: _handle_show_img(test),
        INTERRUPT_INST_USR_RESP: lambda: _handle_user_response(test),
    }

    handler = dispatch.get(instruction)
    if handler:
        handler()
    else:
        raise ValueError(f'Unexpected instruction code: {instruction}')

def _handle_show_result(test: VisionTest, degree: float):
    _LOGGER.debug('Show result')
    show_result(test, degree)

def _handle_start_mov(test: VisionTest, delta: float):
    target = test.cur_distance + (delta / 1000)
    _LOGGER.info(f"Start moving {delta} mm to {round(target, 3)}")

    test.oled.clear()
    test.oled.display()

    msg = f'm{0 if delta > 0 else 1},{abs(delta)}\n'
    _LOGGER.debug(f"sending: {msg.rstrip()}")
    test.motor.write(msg.encode())

    resp = test.motor.readline().decode().strip()
    if resp == 'ok':
        test.cur_distance = round(target, 3)
        _LOGGER.debug(f"Start move got \"ok\"")
    else:
        raise ValueError(f'Unexpected response from start move: {resp}')

    wait_mov(test)
    audio_player.wait_play_done()

def _handle_show_img(test: VisionTest):
    thickness = vision.thickness[int(test.cur_degree * 10) - 1]
    img = draw_circle_with_right_opening(thickness=thickness)
    test.dir = random.randint(0, 3)
    _LOGGER.debug(f"Dir: {test.dir}")
    result = paste_square_image_centered(img.rotate(test.dir * 90))
    show_img(test, result)

def _handle_user_response(test: VisionTest):
    test.got_resp = test_resp(test)
    _LOGGER.info(f'Got test response: {test.got_resp}')


def wait_mov(test: VisionTest):
    resp = test.motor.readline().decode().strip()

    if resp == 'done':
        test.audio.play_async(BEEP_FILE, 'all')
        _LOGGER.info(f"Move done")
    else:
        raise ValueError(f'Unexpected response from wait move: {resp}')

def show_result(test: VisionTest, degree: float) -> None:
    if abs(degree - INTERRUPT_RESULT_MIN) < 0.1:
        _LOGGER.info('Test result: < 0.1')
        d = 0.0
    elif abs(degree - INTERRUPT_RESULT_MAX) < 0.1:
        _LOGGER.info('Test result: >= 1.5')
        d = 1.6
    else:
        _LOGGER.info(f'Test result: degree')
        d = degree

    image = new('1', (128, 64))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(**RESULT_FONT)

    draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
    draw.text((0, 0), RESULT_STRS[test.lang.lang_code], font=font, fill=255)
    draw.text((5, 22), f'{d:0.1f}', font=font, fill = 255)
    test.oled.set_img(image)
    test.oled.display()
    test.audio.play_async(TEST_DONE_FILE, LANGUAGES[test.lang.lang_code])

def show_img(test: VisionTest, img: Image) -> None:
    _LOGGER.info(f'Show image, dir: {test.dir}')
    test.oled.set_img(img)
    test.oled.display()

def test_resp(test: VisionTest) -> bool:
    while True:
        try:
            _LOGGER.info(f'Waiting test resp')
            res = test.stt.get_test_resp(test.lang)
            _LOGGER.info(f'Got response: {res}')
            return  res == test.dir

        except ValueError as e:
            _LOGGER.warning(e.args[0])

def lang_resp(test: VisionTest) -> Language:
    while True:
        try:
            _LOGGER.info(f'Waiting language resp')
            return test.stt.get_lang_resp()

        except ValueError as e:
            _LOGGER.warning(e.args[0])
