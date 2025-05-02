import logging
import os
import sys
import select
from setting import *
from bluetooth.device_manager import BluetoothScanner, connect_device
from bluetooth.classes import Device
from typing import List

logger = logging.getLogger('bt_test')
logger.setLevel(LOGGER_LEVEL)

def clear_screen():
    """清除終端螢幕"""
    os.system('clear' if os.name == 'posix' else 'cls')

def display_devices(devices: List[Device]):
    """顯示設備列表"""
    print("\n找到以下設備：")
    if not devices:
        print("  未找到可連線的設備")
    else:
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device.device_name} ({device.mac_address})")
    print("\n請輸入要連接的設備編號 (1-{})，或按 Enter 繼續掃描: ".format(len(devices)))

def main():
    logger.info("啟動藍牙設備掃描...")
    bt_scanner = BluetoothScanner()
    
    try:
        # 啟動掃描
        bt_scanner.start()
        
        last_devices = []
        while True:
            # 每 5 秒更新設備列表
            devices = bt_scanner.list_devices()
            
            # 僅在設備列表變化時記錄日誌
            if set((d.device_name, d.mac_address) for d in devices) != set((d.device_name, d.mac_address) for d in last_devices):
                logger.info(f"設備列表更新，發現 {len(devices)} 個設備")
                last_devices = devices.copy()
            
            # 清除螢幕並顯示設備
            clear_screen()
            display_devices(devices)
            
            # 使用 select 實現非阻塞輸入（5 秒超時）
            rlist, _, _ = select.select([sys.stdin], [], [], 5)
            if rlist:
                user_input = sys.stdin.readline().strip()
                if user_input:
                    try:
                        choice = int(user_input)
                        if 1 <= choice <= len(devices):
                            selected_device = devices[choice - 1]
                            logger.info(f"正在連線到 {selected_device.device_name}...")
                            if connect_device(selected_device):
                                logger.info(f"成功連線到 {selected_device.device_name}")
                            else:
                                logger.error(f"連線到 {selected_device.device_name} 失敗")
                            break
                        else:
                            logger.error("無效的編號")
                            input("按 Enter 繼續...")
                    except ValueError:
                        logger.error("請輸入有效的數字")
                        input("按 Enter 繼續...")
    
    except KeyboardInterrupt:
        logger.info("用戶終止程式")
    except Exception as e:
        logger.error(f"程式異常: {e}")
    finally:
        # 確保退出時停止掃描
        bt_scanner.stop()
        logger.info("程式結束")

if __name__ == "__main__":
    main()