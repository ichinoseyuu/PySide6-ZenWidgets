import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets import *
from appitem import AppIconItem

class PortableBox(ZStandardFramelessWindow):
    def __init__(self):
        super().__init__()
        print(ZStyleDataManager()._cache)
        self.setupUi()

    def setupUi(self):
        screen_size = QGuiApplication.primaryScreen().size()
        size = QSize(screen_size.width()*0.4,screen_size.height()*0.6)
        self.setMinimumSize(size)
        self.resize(size)
        self.moveCenter()
        self.setWindowTitle("PortableBox")

        self.boxContainer = ZFlowContainer(self.centerWidget())
        self.boxContainer.setLineHeight(72)
        # 创建自定义控件（示例：传入记事本exe路径）
        notepad_path = "C:/Windows/System32/notepad.exe"  # Windows记事本路径
        app_icon = AppIconItem(notepad_path)

        # 选中状态变化示例
        app_icon.selectedChanged.connect(lambda is_selected: print(f"选中状态：{is_selected}"))

        self.boxContainer.addWidget(app_icon)
        self.boxContainer.regDraggableWidget(app_icon)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.boxContainer.resize(self.centerWidget().size())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PortableBox()
    window.show()
    app.exec()