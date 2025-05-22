import time
import threading
from .models import Menu, TextMenuElement, IconMenuElement, IResource, VisionTest
from data.draw import draw_bluetooth_icon, draw_start_icon, draw_volume_icon, cross, check, draw_loading_frames
from bluetooth.classes import Device
from config_manager import get_config_value
from setting import *
import logging
from typing import Callable
from PIL.Image import Image

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
    def wrap_bluetooth_select_callback(cls, res: IResource, bt_device: Device, menu: 'MainMenu') -> Callable[[], int]:
        def wrapped() -> int:
            animation_thread = threading.Thread(target=menu.show_loading_animation)
            animation_thread.start()
            if res.connect_bt_device(bt_device):
                res.bt_device = bt_device
                cls.logger.info(f'Connect to \"{bt_device.device_name}\"')
            else:
                res.bt_device = None
                cls.logger.info(f'Fail to connect \"{bt_device.device_name}\"')
            menu.stop_loading_animation()
            animation_thread.join()
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
    loading_frames: list[Image]
    is_loading: bool
    update_thread: threading.Thread  # 後台更新線程
    stop_update: threading.Event  # 控制更新線程停止
    is_navigating: bool  # 標記是否正在上下切換
    navigation_timer: threading.Timer  # 延遲重置 is_navigating
    oled_lock: threading.Lock  # OLED 訪問鎖

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
        self.loading_frames = draw_loading_frames()
        self.is_loading = False
        self.stop_update = threading.Event()
        self.is_navigating = False
        self.navigation_timer = None
        self.oled_lock = threading.Lock()
        default_device = Device('default', get_config_value('HEADPHONE_DEVICE_MAC') or 'none')
        self.logger.info(f'Connect to default device: {self.res.connect_bt_device(default_device)}')
        self.refresh_bluetooth()

    def start_bluetooth_update(self):
        """啟動後台線程，每 3 秒更新藍牙設備列表"""
        self.stop_update.clear()
        self.update_thread = threading.Thread(target=self._update_bluetooth_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        self.logger.info("Started bluetooth update thread")

    def stop_bluetooth_update(self):
        self.stop_update.set()
        self.logger.info("Requested stop for bluetooth update thread")

    def _update_bluetooth_loop(self):
        """後台循環，每 3 秒更新藍牙設備列表"""
        while not self.stop_update.is_set():
            if self.state == MENU_STATE_BT and not self.is_loading and not self.is_navigating:
                if not self.stop_update.is_set():
                    self.logger.debug("Conditions met, refreshing bluetooth")
                    self.refresh_bluetooth()
            time.sleep(3)

    def _reset_navigation(self):
        """重置 is_navigating 標誌，恢復自動更新"""
        self.is_navigating = False
        self.logger.debug("Navigation ended, resuming bluetooth updates")
        self.navigation_timer = None

    def show_loading_animation(self):
        self.logger.info('Starting loading animation')
        self.is_loading = True
        frame_interval = 0.05
        frame_count = len(self.loading_frames)
        frame_index = 0
        while self.is_loading:
            with self.oled_lock:
                self.res.oled_clear()
                self.res.oled_img(self.loading_frames[frame_index])
                self.res.oled_display()
            frame_index = (frame_index + 1) % frame_count
            time.sleep(frame_interval)

    def stop_loading_animation(self):
        self.logger.info('Stopping loading animation')
        self.is_loading = False
        with self.oled_lock:
            self.res.oled_clear()
            self.res.oled_display()

    def refresh_bluetooth(self):
        self.logger.debug('Refresh bluetooth')
        bluetooth_device_list = self.res.list_bt_device()
        
        current_device_name = None
        if self.bluetooth_menu.item_list and 0 <= self.bluetooth_menu.select_index < len(self.bluetooth_menu.item_list):
            current_device_name = self.bluetooth_menu.item_list[self.bluetooth_menu.select_index].title

        if not bluetooth_device_list:
            bluetooth_ele = [TextMenuElement("No Devices", lambda: MENU_STATE_BT)]
            self.logger.debug('No Bluetooth devices found, setting placeholder')
        else:
            bluetooth_ele = [
                TextMenuElement(
                    text=device.device_name,
                    call_back=CallBacks.wrap_bluetooth_select_callback(self.res, device, self)
                ) for device in bluetooth_device_list
            ]

        self.bluetooth_menu.item_list = bluetooth_ele

        if current_device_name:
            for i, item in enumerate(bluetooth_ele):
                if item.title == current_device_name:
                    self.bluetooth_menu.select_index = i
                    self.logger.debug(f'Restored selection to "{current_device_name}" at index {i}')
                    break
            else:
                self.bluetooth_menu.select_index = 0
                self.logger.debug(f'Device "{current_device_name}" not found, reset to index 0')
        else:
            self.bluetooth_menu.select_index = 0

        if self.bluetooth_menu.select_index >= len(self.bluetooth_menu.item_list):
            self.bluetooth_menu.select_index = max(0, len(self.bluetooth_menu.item_list) - 1)
            self.logger.debug(f'Adjusted select_index to {self.bluetooth_menu.select_index}')

        self.logger.debug(f'Set bluetooth list to {[item.title for item in bluetooth_ele]}')

        # 如果在藍牙選單中，重繪畫面
        if self.state == MENU_STATE_BT:
            with self.oled_lock:
                self.res.oled_clear()
                self.res.oled_img(self.bluetooth_menu.list_img())
                self.res.oled_display()

    def _current_menu(self) -> Menu:
        menus = {
            MENU_STATE_ROOT: self.root_menu,
            MENU_STATE_BT: self.bluetooth_menu,
            MENU_STATE_VOLUME: self.volume_menu
        }
        r = menus.get(self.state)
        if r is None:
            raise ValueError(f'Unknown state: {self.state}')
        return r

    def loop(self):
        self.logger.info(f'Enter loop with cs: {self.state}, ns: {self.ns}')
        if self.res.bt_device is None:
            self.logger.debug('Not connected to device')
            if self.state != MENU_STATE_BT and self.ns != MENU_STATE_BT:
                self.ns = MENU_STATE_ROOT
                self.root_menu.select_index = 1
            self.root_menu.hide_arrow = True
        else:
            self.root_menu.hide_arrow = False

        goto_funcs = {
            MENU_STATE_ROOT: self._goto_root,
            MENU_STATE_BT: self._goto_bt,
            MENU_STATE_VOLUME: self._goto_volume
        }
        goto_func = goto_funcs.get(self.ns)
        if self.state != self.ns:
            if goto_func is None:
                raise ValueError(f'Unknown state: {self.ns}')
            else:
                goto_func()

        self.state = self.ns
        current_menu = self._current_menu()
        self.logger.debug(f'Selected index: {current_menu.select_index}')

        if self.state == MENU_STATE_ROOT and current_menu.select_index == 1:
            if self.res.bt_device is None:
                current_menu.item_list[1].img = cross(draw_bluetooth_icon())
            else:
                current_menu.item_list[1].img = check(draw_bluetooth_icon())

        with self.oled_lock:  # 保護 OLED 訪問
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
        if callee is None:
            raise ValueError(f'Unknown btn: {btn}')
        else:
            if btn in (BTN_UP, BTN_DOWN):
                self.is_navigating = True
                self.logger.debug("Navigation started, pausing bluetooth updates")
                if self.navigation_timer is not None:
                    self.navigation_timer.cancel()
                self.navigation_timer = threading.Timer(3.0, self._reset_navigation)
                self.navigation_timer.start()
            next_state = callee()
            if next_state is not None:
                self.ns = next_state

    def _goto_volume(self):
        self.logger.info('Change to volume')
        self.volume_menu.select_index = self.res.get_volume() // 5

    def _goto_bt(self):
        self.logger.info('Change to bt')
        self.refresh_bluetooth()
        self.start_bluetooth_update()

    def _goto_root(self):
        self.logger.info('Change to root')
        self.stop_bluetooth_update()

    def __del__(self):
        """清理資源"""
        self.stop_bluetooth_update()
        if self.navigation_timer is not None:
            self.navigation_timer.cancel()
        self.logger.info("MainMenu destroyed")