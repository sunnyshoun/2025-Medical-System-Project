from rpi.resource import Resource
from data.draw import draw_circle_with_right_opening, paste_square_image_centered
import time, random

res = Resource()

while True:
    img = paste_square_image_centered(draw_circle_with_right_opening(random.randint(2, 5)).rotate(random.choice([0, 90, 180, 270])))
    res.oled_img(img)
    res.oled_display()
    time.sleep(0.5)
