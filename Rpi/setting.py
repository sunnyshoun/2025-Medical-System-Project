RPI_LOOP_INTERVAL = 0.1  # in second
RPI_SERIAL = {'port': '/dev/ttyS0'}
RPI_START_DISTANCE = 0.1  # in meter
ASK_LANG_FILE = 'ask_lang.wav'
BEEP_FILE = 'beep.wav'
TEST_INTRO_FILE = 'test_intro.wav'
TEST_DONE_FILE = 'test_done.wav'
RECOGNITION_FAIL_FILE = 'recognition_failed.wav'

TEST_START_DEGREE = 0.5
TEST_START_DISTANCE = 0.1

LOGGER_FORMAT = '%(name)-11s:%(levelname)-7s: %(message)s'
LOGGER_LEVEL = 'DEBUG'
LOG_FOLDER = './.log/'
LOG_TIME_FORMAT = '%y%m%d_%H%M%S'

GPIO_SONIC_TRIGGER = 23
GPIO_SONIC_ECHO = 24
GPIO_SONIC_TIMEOUT = 0.04

SONIC_SPEED = 343 # m/s
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

RESULT_STRS = [
    '您的視力: ',
    '恁ㄟ視力: ',
    'Your vision: ',
    'あなたの視力: '
]
RESULT_FONT = {'font': './data/NotoSansCJK-Regular.ttc', 'size': 20}
MENU_FONT = {'font': './data/NotoSansCJK-Regular.ttc', 'size': 15}
MENU_MAX_TEXT_LEN = 14
MENU_TEXT_HEIGHT = 20
 

# === Define ===
INTERRUPT_INST_SHOW_RESULT = 0
INTERRUPT_INST_START_MOV = 2
INTERRUPT_INST_SHOW_IMG = 3
INTERRUPT_INST_USR_RESP = 4

INTERRUPT_RESULT_MIN = -1.0
INTERRUPT_RESULT_MAX = 2.0

LANG_ZH = 0
LANG_TW = 1
LANG_EN = 2
LANG_JP = 3

LANGUAGES = [
    'zh',
    'tw',
    'en',
    'jp'
]

MENU_STATE_ROOT = 0
MENU_STATE_BT = 1
MENU_STATE_VOLUME = 2

BTN_UP = 16
BTN_CONFIRM = 20
BTN_DOWN = 31
