from .models import Menu, TextMenuElement, IconMenuElement, IResource, VisionTest
from data.draw import draw_bluetooth_icon, draw_start_icon, draw_volume_icon, cross, check
from bluetooth.classes import Device
from config_manager import get_config_value
from setting import *
import logging
from typing import Callable

class CallBacks:
    logger = logging.getLogger('CallBacks')

    @classmethod    
    def bluetooth_enter_callback(cls) -> int:
        cls.logger.info('Enter bluetooth')
        return MENU_STATE_BT
    
    @classmethod    
    def volume_enter_callback(cls) -> int:
        cls.logger.info('Enter volume')
        return MENU_STATE_VOLUME
    
    @classmethod
    def wrap_bluetooth_select_callback(cls, res: IResource, bt_device: Device) -> Callable[[], int]:
        def wrapped() -> int:
            if res.connect_bt_device(bt_device):
                res.bt_device = bt_device
                cls.logger.info(f'Connect to \"{bt_device.device_name}\"')
            else:
                res.bt_device = None
                cls.logger.info(f'Fail to connect \"{bt_device.device_name}\"')
            return MENU_STATE_ROOT
        
        return wrapped
    
    @classmethod
    def wrap_volume_select_callback(cls, res: IResource, p: int) -> Callable[[], int]:
        def wrapped() -> int:
            res.set_volume(p)
            cls.logger.info(f'Set volume to {p}%')
            return MENU_STATE_ROOT
        
        return wrapped
    
class MainMenu:
    root_menu: Menu
    bluetooth_menu: Menu
    volume_menu: Menu

    state: int
    ns: int
    res: IResource
    logger = logging.getLogger('MainMenu')
    logger.setLevel(LOGGER_LEVEL)

    def __init__(self, tester_func: Callable[[], int], res: IResource):
        root_ele = [
            IconMenuElement(draw_start_icon(), tester_func, 'start'),
            IconMenuElement(draw_bluetooth_icon(), CallBacks.bluetooth_enter_callback, 'bluetooth'),
            IconMenuElement(draw_volume_icon(), CallBacks.volume_enter_callback, 'volume')
        ]
        self.root_menu = Menu(root_ele, SCREEN_HEIGHT)

        self.bluetooth_menu = Menu([], MENU_TEXT_HEIGHT)

        volume_ele = [
            TextMenuElement(f'{p}%', CallBacks.wrap_volume_select_callback(res, p)) for p in range(0, 101, 5)
        ]
        self.volume_menu = Menu(volume_ele, MENU_TEXT_HEIGHT)
        

        self.state = MENU_STATE_ROOT
        self.ns = MENU_STATE_ROOT
        self.res = res

        default_device = Device('default', get_config_value('HEADPHONE_DEVICE_MAC'))
        
        self.logger.info(f'Connect to default device: {self.res.connect_bt_device(default_device)}')

    def _current_menu(self) -> Menu:
        menus = {
            MENU_STATE_ROOT: self.root_menu,
            MENU_STATE_BT: self.bluetooth_menu,
            MENU_STATE_VOLUME: self.volume_menu
        }

        r = menus.get(self.state)
        if r == None:
            raise ValueError(f'Unknown state: {self.state}')
        else:
            return r
    
    def refresh_bluetooth(self):
        self.logger.debug('Refresh bluetooth')
        bluetooth_device_list = self.res.list_bt_device()
        bluetooth_ele = [
            TextMenuElement(text=device.device_name, call_back=CallBacks.wrap_bluetooth_select_callback(self.res, device)) for device in bluetooth_device_list
        ]
        self.bluetooth_menu.item_list = bluetooth_ele
        self.logger.debug(f'Set bluetooth list to {[f"{t.title}({d.device_name})" for t, d in zip(bluetooth_ele, bluetooth_device_list)]}')

    def loop(self):
        self.logger.info(f'Enter loop with cs: {self.state}, ns: {self.ns}')
        if self.res.bt_device == None:
            self.logger.debug('Not connected to device')
            if self.state != MENU_STATE_BT and self.ns != MENU_STATE_BT:
                self.ns = MENU_STATE_ROOT
                self.root_menu.select_index = 1

        goto_funcs = {
            MENU_STATE_ROOT: self._goto_root,
            MENU_STATE_BT: self._goto_bt,
            MENU_STATE_VOLUME: self._goto_volume
        }
        goto_func = goto_funcs.get(self.ns)
        if self.state != self.ns:
            if goto_func == None:
                ValueError(f'Unknown state: {self.ns}')
            else:
                goto_func()

        self.state = self.ns
        current_menu = self._current_menu()
        self.logger.debug(f'Selected index: {current_menu.select_index}')

        if self.state == MENU_STATE_ROOT and current_menu.select_index == 1:
            if self.res.bt_device == None:
                current_menu.item_list[1].img = cross(draw_bluetooth_icon())
            else:
                current_menu.item_list[1].img = check(draw_bluetooth_icon())

        self.res.oled_clear()
        self.res.oled_img(current_menu.list_img())
        self.res.oled_display()

        btn = self.res.read_btn()
        self.logger.info(f'Got btn {btn}')
        btn_events = {
            BTN_UP: current_menu.move_up,
            BTN_CONFIRM: current_menu.select,
            BTN_DOWN: current_menu.move_down
        }
        callee = btn_events.get(btn)
        if callee == None:
            raise ValueError(f'Unknown btn: {btn}')
        else:
            callee()

    def _goto_volume(self):
        self.logger.info('Change to volume')
        self.volume_menu.select_index = self.res.get_volume() // 5

    def _goto_bt(self):
        self.logger.info('Change to bt')
        self.refresh_bluetooth()
        try:
            self.bluetooth_menu.select_index = self.bluetooth_menu.item_list.index(get_config_value('HEADPHONE_DEVICE_MAC'))
        except:
            self.bluetooth_menu.select_index = 0
    
    def _goto_root(self):
        self.logger.info('Change to root')
