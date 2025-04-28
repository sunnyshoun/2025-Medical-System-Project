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

# 使用範例
if __name__ == "__main__":
    img = draw_circle_with_right_opening(thickness=1)
    
    # 呼叫函數，貼到 128x64 的畫布中
    result = paste_square_image_centered(img)
    result.show()
