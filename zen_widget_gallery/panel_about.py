from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout,QSizePolicy
from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QFont
from ZenWidgets import *

class PanelAbout(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelAbout')
        self.setLayout(ZVBoxLayout(self, QMargins(40, 30, 40, 30), 30))
        self._setup_ui()

    def _setup_ui(self):
        self.text = ZHeadLine(parent=self, text='关于', display_indicator=True)
        self.text.setFont(QFont('Microsoft YaHei', 20, QFont.Bold))
        self.text.setPadding(ZPadding(6, 6, 6, 6))
        self.layout().addWidget(self.text)

        text= '''    ZenWidgets 是一款为追求极致用户体验的开发者打造的现代化风格的组件库，它基于 PySide6 中的 QWidget 架构设计而成，在保持界面简洁的同时，融入了流畅的交互动画。与 QWidget 不同，ZenWidgets 支持动态切换主题和自定义主题配色，通过舍弃对 QSS 样式表的依赖，采用完全自定义的绘制逻辑，让UI具有流畅的交互动画且风格更符合现代审美。目前，ZenWidgets 已提供覆盖基础界面开发需求的核心组件。ZenWidgets 组件库正处于持续进化中，未来计划加入更多实用模块，致力于为 PySide6 开发者提供一套既美观又高效的界面解决方案，在 QWidget 界面开发上变得更简单快捷。'''

        self.textblock_1 = ZTextBlock(self, text=text)
        self.layout().addWidget(self.textblock_1)