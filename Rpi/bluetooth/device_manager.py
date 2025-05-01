import subprocess
import re
import time, logging
from typing import List
from .classes import Device
from config_manager import load_config, save_config

logger = logging.getLogger('deviceManager')

def run_command(command, timeout=10):
    """執行 shell 命令並返回輸出"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"命令執行失敗: {command}\n錯誤: {e.stderr.strip()}")
        return None
    except subprocess.TimeoutExpired:
        logger.error(f"命令超時: {command}")
        return None

def list_devices() -> List[Device]:
    """列出所有藍牙設備（已連線、已配對、新設備）"""
    devices = []
    
    # 獲取已配對設備
    paired_output = run_command("echo 'devices Paired' | bluetoothctl")
    paired_devices = {}
    if paired_output:
        for line in paired_output.splitlines():
            match = re.match(r"Device ([0-9A-F:]+) (.+)", line)
            if match:
                mac, name = match.groups()
                mac_formatted = mac.replace(":", "_")
                connected = run_command(f"echo 'info {mac}' | bluetoothctl | grep 'Connected: yes'") is not None
                paired_devices[mac_formatted] = {"name": name, "connected": connected}
                devices.append(Device(device_name=name, mac_address=mac_formatted))

    # 掃描新設備（短暫掃描 5 秒）
    new_devices = {}
    scan_process = subprocess.Popen(
        "bluetoothctl scan on", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    start_time = time.time()
    try:
        while time.time() - start_time < 5:
            stdout_line = scan_process.stdout.readline().strip()
            if stdout_line:
                match = re.search(r"\[NEW\] Device ([0-9A-F:]+) (.+)", stdout_line)
                if match:
                    mac, name = match.groups()
                    mac_formatted = mac.replace(":", "_")
                    if mac_formatted not in paired_devices:
                        new_devices[mac_formatted] = {"name": name, "connected": False}
                        devices.append(Device(device_name=name, mac_address=mac_formatted))
            time.sleep(0.1)
    finally:
        run_command("echo 'scan off' | bluetoothctl")
        scan_process.terminate()

    return devices

def connect_device(device: Device) -> bool:
    """連線設備、設定為 HFP、設定預設輸入/輸出，並更新 config"""
    config = load_config()
    mac = device.mac_address.replace("_", ":")  # 轉為 bluetoothctl 需要的格式

    try:
        # 步驟 1: 連線設備
        logger.info(f"正在連線到設備 {device.device_name} ({mac})...")
        run_command(f"echo 'trust {mac}' | bluetoothctl")
        run_command(f"echo 'pair {mac}' | bluetoothctl")
        run_command(f"echo 'connect {mac}' | bluetoothctl")
        time.sleep(3)
        if not run_command(f"echo 'info {mac}' | bluetoothctl | grep 'Connected: yes'"):
            logger.warning("設備連線失敗")
            return False

        # 步驟 2: 設定為 HFP 模式
        card_name = f"bluez_card.{device.mac_address}"
        cards = run_command("pactl list cards short")
        if not (cards and card_name in cards):
            logger.warning(f"無法設定 HFP 模式，未找到卡 {card_name}")
            return False
        run_command(f"pactl set-card-profile {card_name} headset_head_unit")
        time.sleep(1)

        # 步驟 3: 設定預設輸入和輸出
        sink_name = f"bluez_sink.{device.mac_address}.headset_head_unit"
        source_name = f"bluez_source.{device.mac_address}.headset_head_unit"
        run_command(f"pactl set-default-sink {sink_name}")
        run_command(f"pactl set-default-source {source_name}")
        sinks = run_command("pactl list sinks short")
        sources = run_command("pactl list sources short")
        if not (sinks and sources and sink_name in sinks and source_name in sources):
            logger.warning(f"設定預設音訊設備失敗，Sink: {sink_name}, Source: {source_name}")
            return False

        # 步驟 4: 更新 config.json 的 HEADPHONE_DEVICE_MAC
        config["HEADPHONE_DEVICE_MAC"] = device.mac_address
        save_config(config)
        logger.info("設備連線並設定成功")
        return True
    except Exception as e:
        logger.error(f"連線或設定設備失敗: {str(e)}")
        return False

def set_device_volume(volume: int) -> bool:
    """設定預設設備的播放音量並更新 config 的 VOLUME"""
    if not 0 <= volume <= 100:
        logger.warning("音量必須在 0 到 100 之間")
        return False

    config = load_config()
    mac_address = config.get("HEADPHONE_DEVICE_MAC")
    if not mac_address:
        logger.warning("未找到 HEADPHONE_DEVICE_MAC 配置")
        return False

    try:
        # 設定播放音量
        volume_str = f"{volume}%"
        sink_name = f"bluez_sink.{mac_address}.headset_head_unit"
        run_command(f"pactl set-sink-volume {sink_name} {volume_str}")

        # 更新 config.json 的 VOLUME
        config["VOLUME"] = volume_str
        save_config(config)
        logger.info(f"播放音量設定為 {volume_str}")
        return True
    except Exception as e:
        logger.error(f"設定播放音量失敗: {str(e)}")
        return False