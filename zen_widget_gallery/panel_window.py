from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout,QSizePolicy
from PySide6.QtCore import Qt, QMargins,QPoint,QSize
from PySide6.QtGui import QFont, QIcon, QColor
from ZenWidgets import *

class PanelWindow(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelWindow')
        self.setLayout(ZVBoxLayout(self, QMargins(40, 30, 40, 30), 30, Qt.AlignmentFlag.AlignTop))
        self._setup_ui()


    def _setup_ui(self):
        self.title = ZHeadLine(self, text='窗口', display_indicator=True)
        self.title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))
        self.title.setPadding(ZPadding(6, 0, 6, 6))
        self.layout().addWidget(self.title)
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        card = ZCard(self)
        self.layout().addWidget(card)

        title = ZHeadLine(self, text='ZDialog')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)
        card.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.test_btn = ZButton(card, text="打开对话框")
        self.test_btn.clicked.connect(self.open_dialog)
        card.layout().addWidget(self.test_btn)


    def open_dialog(self):
        dialog = ZDialog(self.test_btn, title="基尼钛煤！", message='再多看一眼就会爆炸！')
        print(dialog.exec())

