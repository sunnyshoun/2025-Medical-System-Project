import os
import json
import logging

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
logger = logging.getLogger('configManager')

def load_config():
    """讀取 config.json 檔案"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"錯誤：找不到 {CONFIG_PATH}")
        return {}
    except json.JSONDecodeError:
        logger.error("錯誤：config.json 格式無效")
        return {}

def save_config(config):
    """儲存配置到 config.json"""
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"儲存配置失敗：{str(e)}")

def get_config_value(key, default=None):
    """獲取指定鍵的值"""
    config = load_config()
    return config.get(key, default)

def update_config_value(key, value):
    """更新配置中的鍵值"""
    config = load_config()
    config[key] = value
    save_config(config)

if __name__ == "__main__":
    example_config = {
        "HEADPHONE_DEVICE_MAC": "14:98:77:EC:59:02",
        "VOLUME": "50%"
    }
    # 儲存範例配置
    save_config(example_config)
    
    # 讀取配置
    print("配置：", load_config())
    
    # 更新配置
    update_config_value("HEADPHONE_DEVICE_MAC", None)
    print("配置：", load_config())