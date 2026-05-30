from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout,QSizePolicy
from PySide6.QtCore import Qt, QMargins,QPoint,QSize
from PySide6.QtGui import QFont, QIcon, QColor
from ZenWidgets import *

class PanelDebug(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelInfo')
        self.setLayout(ZVBoxLayout(self, QMargins(40, 30, 40, 30), 30, Qt.AlignmentFlag.AlignTop))
        self._setup_ui()


    def _setup_ui(self):
        self.title = ZHeadLine(self, text='调试设置', display_indicator=True)
        self.title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))
        self.title.setPadding(ZPadding(6, 0, 6, 6))
        self.layout().addWidget(self.title)


        self.btn_drawrect = ZButton(self, text='绘制矩形边框')
        def _debug():
            self.btn_drawrect.setText('绘制矩形边框' if ZDebug.draw_rect else '取消绘制')
            ZDebug.draw_rect = not ZDebug.draw_rect
            self.window().repaint()
            ZGlobal.themeManager.updateStyle()
        self.btn_drawrect.clicked.connect(_debug)
        self.layout().addWidget(self.btn_drawrect)