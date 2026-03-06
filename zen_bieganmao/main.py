import sys
import random
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets import *
from image_rc import *
from popupmessage import PopupMessage

class ZenBieGanMao(ZStandardFramelessWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.showMaximized()

    def setupUi(self):
        self.setWindowTitle("别感冒!")
        self.tips = [
            '多喝水哦~','保持微笑~','元气满满！','加油哦~',
            '记得吃水果~','保持好心情~', '顺顺利利！','早点休息~',
            '烦恼都消失！','天天开心！','别熬夜！',
            '别感冒！','别感冒！','别感冒！','别感冒！','别感冒！'
        ]
        self.light_bg_color = [
            'lightpink','skyblue','lightgreen','lightyellow',
            'lavender','plum','lightcoral','bisque','aquamarine',
            'mistyrose','honeydew','lavenderblush','oldlace'
        ]
        self.dark_bg_color = [
            'darkred', 'darkblue', 'darkgreen', 'darkslategray',
            'indigo', 'purple', 'saddlebrown', 'darkcyan',
            'darkorchid', 'midnightblue', 'darkmagenta', 'teal',
            'navy', 'maroon', 'olive'
        ]
        self.popupstack = []
        self.popup_count = 0
        self.max_popups = 120
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.generate_popup)
        self.start_random_timer()

    def start_random_timer(self):
        self.timer.start(random.randint(50, 100))

    def generate_popup(self):
        if self.popup_count >= self.max_popups:
            self.timer.stop()
            ZGlobal.themeManager.setTheme(ZTheme.Dark)
            image = ZImage(self,image_path=':/bieganmao.jpg')
            image.widgetRectCtrl.scaleIn(QRect(self.width()//2-200, self.height()//2-200, 400, 400))
            image.show()
            return
        colors = self.light_bg_color if ZGlobal.themeManager.getThemeName() == 'Light' else self.dark_bg_color
        color = random.choice(colors)
        tip = random.choice(self.tips)
        x = random.randint(0, self.width() - 100)
        y = random.randint(32, self.height() - 100)
        popup = PopupMessage(QColor(color), tip, self)
        popup.move(x, y)
        popup.show()
        self.popupstack.append(popup)
        self.popup_count += 1
        self.start_random_timer()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ZenBieGanMao()
    window.show()
    app.exec()