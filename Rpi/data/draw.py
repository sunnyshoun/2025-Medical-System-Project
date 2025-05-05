import math
from PIL import Image, ImageDraw

def draw_circle_with_right_opening(thickness=10, save_as=None, background=0):
    size = thickness * 4
    img_padding = 1 if thickness < 6 else 0
    img = Image.new('L', (size + thickness//4 + img_padding, size + thickness//4 + img_padding), background)  # 黑底圖像
    draw = ImageDraw.Draw(img)

    # 畫白色的圓框（用兩個圓疊出圓環效果）
    outer_bbox = [0, 0, size, size]
    inner_padding = thickness
    inner_bbox = [inner_padding, inner_padding, size - inner_padding, size - inner_padding]

    draw.ellipse(outer_bbox, fill=255)  # 外圓：白色
    draw.ellipse(inner_bbox, fill=0)    # 內圓：黑色，產生厚度效果

    # 畫黑色矩形遮住右側，產生開口
    draw.rectangle([size//2, (size - thickness)//2, size, (size + thickness)//2], fill=0)

    if save_as:
        img.save(save_as)

    return img

def paste_square_image_centered(src_img: Image.Image, target_size=(128, 64), background=0):
    # 檢查是否為正方形
    if src_img.width != src_img.height:
        raise ValueError("Source image is not square: {0}x{1}".format(src_img.width, src_img.height))

    # 建立新的 128x64 畫布
    canvas = Image.new('L', target_size, background)

    # 計算置中位置
    x_offset = (target_size[0] - src_img.width) // 2
    y_offset = (target_size[1] - src_img.height) // 2

    # 貼上圖片
    canvas.paste(src_img, (x_offset, y_offset))

    return canvas

def draw_loading_frames() -> list[Image.Image]:
    """生成5個圓點向上跳動的動畫（12幀，20 FPS）"""
    frames = []
    num_dots = 5  # 圓點數量
    dot_radius = 4  # 圓點半徑
    spacing = 16  # 圓點間距（減小以避免裁切）
    jump_height = 10  # 最大跳動高度
    frame_count = 12  # 總幀數
    size = spacing * (num_dots - 1) + dot_radius * 2 + 8  # 畫布寬度，增加8像素邊距
    base_y = 32  # 基準Y座標（螢幕中心）
    for frame in range(frame_count):
        img = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(img)
        phase = frame * (2 * math.pi / frame_count)  # 每幀相位
        offset_x = dot_radius + 6  # 左邊距，增加到6像素
        for i in range(num_dots):
            # 計算圓點X座標（水平排列）
            x = offset_x + i * spacing
            # 計算圓點Y座標（正弦波跳動）
            offset = (i * 2 * math.pi / num_dots) + phase
            y_offset = math.sin(offset) * jump_height
            y = base_y - y_offset  # 向上跳動（Y減小）
            draw.ellipse(
                [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                fill=255
            )
        # 貼到128x64畫布中央
        canvas = paste_square_image_centered(img, target_size=(128, 64))
        frames.append(canvas)
    return frames

def draw_bluetooth_icon() -> Image.Image:
    img = Image.new('1', (128, 64), 0)
    draw = ImageDraw.Draw(img)
    
    cx, cy = 64, 32  # 中心點

    # 藍牙標誌主要結構
    top = (cx, cy - 20)
    bottom = (cx, cy + 20)
    right_upper = (cx + 10, cy - 10)
    right_lower = (cx + 10, cy + 10)
    left_upper = (cx - 10, cy - 10)
    left_lower = (cx - 10, cy + 10)
    
    # 主幹線
    draw.line([cx, cy-21, cx, cy+21], fill=1, width=3)

    draw.line([top, right_upper], fill=1, width=3)
    draw.line([right_upper, left_lower], fill=1, width=3)

    draw.line([bottom, right_lower], fill=1, width=3)
    draw.line([right_lower, left_upper], fill=1, width=3)

    return img

def draw_volume_icon() -> Image.Image:
    img = Image.new('1', (128, 64), 0)
    draw = ImageDraw.Draw(img)

    # 喇叭
    draw.polygon([(40, 26), (50, 26), (58, 20), (58, 44), (50, 38), (40, 38)], fill=1)

    # 聲波
    draw.arc((57, 20, 72, 44), start=300, end=60, fill=1, width=2)
    draw.arc((67, 16, 82, 48), start=300, end=60, fill=1, width=2)
    return img

def draw_start_icon() -> Image.Image:
    img = Image.new('1', (128, 64), 0)
    draw = ImageDraw.Draw(img)
    # 畫一個「播放」三角形
    triangle = [(54, 22), (54, 42), (74, 32)]  # 向右的三角形
    draw.polygon(triangle, fill=1)
    return img

def check(img: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(img)

    # 畫勾：像個對號 ✓
    draw.line([(5, 15), (10, 20)], fill="green", width=2)
    draw.line([(10, 20), (20, 5)], fill="green", width=2)

    return img

def cross(img: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(img)

    # 畫叉：像個 X
    draw.line([(5, 5), (20, 20)], fill="red", width=2)
    draw.line([(20, 5), (5, 20)], fill="red", width=2)

    return img

# 使用範例
if __name__ == "__main__":
    img = draw_circle_with_right_opening(thickness=1)
    
    # 呼叫函數，貼到 128x64 的畫布中
    result = paste_square_image_centered(img)
    result.show()
