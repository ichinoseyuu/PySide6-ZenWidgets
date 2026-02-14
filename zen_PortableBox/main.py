import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets import *
from appitem import AppIconItem

class PortableBox(ZStandardFramelessWindow):
    def __init__(self):
        super().__init__()
        QApplication.setDoubleClickInterval(500)  # 设置双击间隔为500毫秒
        self.setupUi()

    def setupUi(self):
        screen_size = QGuiApplication.primaryScreen().size()
        size = QSize(screen_size.width()*0.4,screen_size.height()*0.6)
        self.setMinimumSize(size)
        self.resize(size)
        self.moveCenter()
        self.setWindowTitle("PortableBox")
        self._apps: ZExclusiveToggleGroup = ZExclusiveToggleGroup(self, allow_uncheck=True)  # 管理AppIconItem的选中状态

        self.boxContainer = ZFlowContainer(self.centerWidget())
        self.boxContainer.setLineHeight(72)

        app_notepad = AppIconItem(parent=self, exe_path="C:/Windows/System32/notepad.exe", app_name="Notepad")
        app_notepad.toggled.connect(self._select_Change_handler)
        self._apps.addWidget(app_notepad,set_first_checked=False)

        self.boxContainer.addWidget(app_notepad)
        self.boxContainer.regDraggableWidget(app_notepad)

        app_calculator = AppIconItem(parent=self, exe_path="C:/Windows/System32/calc.exe", app_name="Calculator")
        app_calculator.toggled.connect(self._select_Change_handler)
        self._apps.addWidget(app_calculator)
        self.boxContainer.addWidget(app_calculator)
        self.boxContainer.regDraggableWidget(app_calculator)


        app_edge = AppIconItem(parent=self, exe_path="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", app_name="Edge")
        app_edge.toggled.connect(self._select_Change_handler)
        self._apps.addWidget(app_edge)
        self.boxContainer.addWidget(app_edge)
        self.boxContainer.regDraggableWidget(app_edge)


    def _select_Change_handler(self, checked: bool):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.boxContainer.resize(self.centerWidget().size())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PortableBox()
    window.show()
    app.exec()