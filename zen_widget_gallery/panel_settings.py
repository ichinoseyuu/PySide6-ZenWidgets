from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt,QMargins
from PySide6.QtGui import QFont
from ZenWidgets import *

class PanelSettings(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelSettings')
        self.setLayout(ZVBoxLayout(self, QMargins(40, 30, 40, 30), 30, Qt.AlignmentFlag.AlignTop))
        self._setup_ui()

    def layout(self) -> ZVBoxLayout:
        return super().layout()

    def _setup_ui(self):
        self.text = ZHeadLine(self, text='设置', display_indicator=True)
        self.text.setFont(QFont('Microsoft YaHei', 20, QFont.Bold))
        self.text.setPadding(ZPadding(6, 0, 6, 6))
        self.layout().addWidget(self.text)

        self.hcontainer = ZHContainer(self)
        self.hcontainer.margin = QMargins(10, 10, 10, 10)
        self.hcontainer.alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        self.layout().addWidget(self.hcontainer)

        self.text_theme_set = ZHeadLine(self.hcontainer, text='主题：')
        self.text_theme_set.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Normal))
        self.hcontainer.addWidget(self.text_theme_set)

        self.btn_theme_set_1 = ZToggleButton(self.hcontainer, text='浅色')
        self.btn_theme_set_1.setButtonGroup(True)
        self.btn_theme_set_1.clicked.connect(lambda: ZGlobal.themeManager.setTheme(ZTheme.Light))
        self.hcontainer.addWidget(self.btn_theme_set_1)

        self.btn_theme_set_2 = ZToggleButton(self.hcontainer, text='深色')
        self.btn_theme_set_2.setButtonGroup(True)
        self.btn_theme_set_2.clicked.connect(lambda: ZGlobal.themeManager.setTheme(ZTheme.Dark))
        self.hcontainer.addWidget(self.btn_theme_set_2)

        self.btn_theme_set_3 = ZToggleButton(self.hcontainer, text='跟随系统')
        self.btn_theme_set_3.setButtonGroup(True)
        self.btn_theme_set_3.clicked.connect(lambda: ZGlobal.themeManager.setThemeMode(ZThemeMode.FollowSystem))
        self.hcontainer.addWidget(self.btn_theme_set_3)
        self.theme_btn_group = ZExclusiveToggleGroup(self.hcontainer)
        self.theme_btn_group.addWidget(self.btn_theme_set_1)
        self.theme_btn_group.addWidget(self.btn_theme_set_2)
        self.theme_btn_group.addWidget(self.btn_theme_set_3)




