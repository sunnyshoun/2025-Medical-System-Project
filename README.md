# 2025-Medical-System-Project

## Raspberry Pi Directory

```
Rpi/
├── audio/
│   ├── audioFiles/
│   │   ├── all/
│   │   ├── en/
│   │   ├── jp/
│   │   ├── tw/
│   │   ├── zh/
│   ├── __init__.py
│   ├── classes.py
│   ├── language_detection.py
│   ├── player.py
│   ├── recognizer.py
│   ├── recorder.py
├── bluetooth/
│   ├── __init__.py
│   ├── classes.py
│   ├── device_manager.py
├── data/
│   ├── __init__.py
│   ├── draw.py
│   ├── NotoSansCJK-Regular.ttc
│   ├── vision.py
├── rpi/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── menus.py
│   │   ├── testers.py
│   ├── __init__.py
│   ├── interrupt.py
│   ├── menu.py
│   ├── resource.py
│   ├── tester.py
├── test/
│   ├── bunch of testing ...
├── config_manager.py
├── config.json
├── main.py (Program Entrance)
├── requirements.txt
├── setting.py
```

## Note

### Menu
|            | MENU_STATE_ROOT | MENU_STATE_BT | MENU_STATE_VOLUME |
|------------|-----------------|---------------|-------------------|
| no device  | root, ind=1     | bt, kp ind    | root, ind=1       |
| has device | root, kp ind    | bt, kp ind    | volume, kp ind    |

### Flow Charts
```mermaid
---
title: Main flow
---
flowchart TD
    set0((啟動程式))
    set1{是否連到裝置？}
    set2{{cs == bt ? kp : ns = root, ind = 1}}
    set3{{kp ns}}
    set6[cs = ns, 重整列表, 初始化目錄]
    act0[/等待按鍵輸入/]
    act1["ns = list[index].call_back()"]
    act4{{index++/index--}}
    end0[下一輪]
    set0 --> set1
    set1 -- 是 --> set3
    set1 -- 否 --> set2
    set3 --> set6
    set2 --> set6
    set6 --> act0
    act0 -- 確認 --> act1
    act0 -- 上/下 --> act4
    act1 --> end0
    act4 --> end0
    end0 --> set1
```
---
```mermaid
---
title: Test flow
---
flowchart TD
    set0((開始測試))
    set1{{cur_degree=0.5, max_degree=-1, lang=input}}
    set2[/使用者選擇語言/]
    act0{0.1 <= cur_degree <= 1.5 ?}
    end1{max_degree < 0 ?}
    act1[/顯示對應度數圖像，等待輸入/]
    act2{使用者是否看得清楚？}
    act3{{max_degree=cur_degree, cur_degree++}}
    act4{max_degree < 0 ?}
    act5{{cur_degree--}}
    end2([結束測試，度數大於最高值])
    end3([結束測試，度數小於最低值])
    end4([結束測試，return max_degree])
    iter[下一輪測量]
    act3 --> iter
    set0 --> set2
    set2 --> set1
    set1 --> act0
    act0 -- 否 --> end1
    end1 -- 否 --> end2
    end1 -- 是 --> end3
    act0 -- 是 --> act1
    act1 --> act2
    act2 -- 否 --> act4
    act2 -- 是 --> act3
    act4 -- 否 --> end4
    act4 -- 是 --> act5
    act5 --> iter
    iter --> act0
```

TODO 優化專案架構至下方樣式
```
Rpi/
├── src/                          # 將主要程式碼集中在 src 目錄下
│   ├── audio/                    # 音訊相關模組
│   │   ├── __init__.py
│   │   ├── models.py             # 將 classes.py 改名為 models.py，統一命名
│   │   ├── detection.py          # 將 language_detection.py 簡化命名
│   │   ├── player.py
│   │   ├── recognizer.py
│   │   ├── recorder.py
│   ├── bluetooth/                 # 藍牙相關模組
│   │   ├── __init__.py
│   │   ├── models.py             # 將 classes.py 改名為 models.py
│   │   ├── manager.py            # 將 device_manager.py 改名為 manager.py
│   ├── data/                     # 靜態資料與資源
│   │   ├── __init__.py
│   │   ├── draw.py
│   │   ├── vision.py
│   │   ├── NotoSansCJK-Regular.ttc
│   ├── hardwares/                # 樹莓派硬體相關模組
│   │   ├── __init__.py
│   │   ├── motor.py
│   │   ├── oled.py
│   │   ├── sonic.py
│   │   ├── button.py
│   ├── rpi/                      # 樹莓派軟體相關模組
│   │   ├── __init__.py
│   │   ├── models/               # 將 models 目錄保留
│   │   │   ├── __init__.py
│   │   │   ├── menus.py
│   │   │   ├── testers.py
│   │   ├── interrupt.py
│   │   ├── menu.py
│   │   ├── resource.py
│   │   ├── tester.py
│   ├── config/                    # 配置相關模組
│   │   ├── __init__.py
│   │   ├── manager.py            # 將 config_manager.py 改名為 manager.py
│   ├── assets/                   # 靜態資源（音訊檔案等）
│   │   ├── audio/                # 將 audioFiles 改名為 audio
│   │   │   ├── all/
│   │   │   ├── en/
│   │   │   ├── jp/
│   │   │   ├── tw/
│   │   │   ├── zh/
│   ├── main.py                   # 程式入口
├── tests/                        # 測試目錄（將 test 改名為 tests，遵循慣例）
│   ├── unit/                     # 單元測試
│   ├── integration/              # 整合測試
│   ├── __init__.py
├── config.json                   # 配置檔案保留在根目錄
├── requirements.txt              # 依賴清單
├── settings.py                   # 將 setting.py 改名為 settings.py（複數形式更符合慣例）
├── README.md                     # 新增專案說明文件
├── LICENSE                       # 新增授權文件
├── .gitignore                    # 新增 Git 忽略文件
```