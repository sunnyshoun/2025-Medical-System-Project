from rpi.model import Menu, MenuElement, TextMenuElement
import os, logging

logging.basicConfig(level='DEBUG')

os.chdir('./Rpi')
eles: list[TextMenuElement] = []
ele = TextMenuElement('asdasd', lambda: print('asdasd'))
eles.append(ele)
ele = TextMenuElement('asdasdasdasdasd', lambda: print('asdasd'))
eles.append(ele)
ele = TextMenuElement('ㄚㄚㄚㄚㄚㄚ', lambda: print('asdasd'))
eles.append(ele)
ele = TextMenuElement('ㄚ1ㄚㄚㄚㄚㄚㄚ1', lambda: print('asdasd'))
eles.append(ele)

menu = Menu(eles, ele.HEIGHT)
menu.list_img().show()
menu.move_down()
menu.list_img().show()
menu.move_down()
menu.list_img().show()
menu.move_down()
menu.list_img().show()
menu.move_down()
menu.list_img().show()
