# 2025-Medical-System-Project

## Directory

- Rpi
  - audio
    - classes.py
    - language_detection.py
    - player.py
    - recognizer.py
    - recorder.py
  - data
    - draw.py
    - vision.py
  - rpi
    - interrupt.py
    - models
      - Menus.py
      - Testers.py
    - resource.py
    - tester.py
  - test
    - bunch of testing ...
  - setting.py

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