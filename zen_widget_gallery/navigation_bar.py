from PySide6.QtCore import Qt,QSize,QPoint
from PySide6.QtGui import QIcon
from ZenWidgets import *

class NavigationBar(ZNavigationBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._setup_ui()

    def _setup_ui(self):
        iconPack = ZGlobal.iconPack
        icon1 = QIcon()
        icon1.addPixmap(iconPack.toPixmap("ic_fluent_home_regular"), QIcon.Mode.Normal, QIcon.State.Off)
        icon1.addPixmap(iconPack.toPixmap("ic_fluent_home_filled"), QIcon.Mode.Normal, QIcon.State.On)
        self.addToggleButton(name="btnHome", icon=icon1, tooltip="主页", panel=self.panel())

        icon2 = QIcon()
        icon2.addPixmap(iconPack.toPixmap("ic_fluent_cube_regular"), QIcon.Mode.Normal, QIcon.State.Off)
        icon2.addPixmap(iconPack.toPixmap("ic_fluent_cube_filled"), QIcon.Mode.Normal, QIcon.State.On)
        self.addToggleButton(name="btnWidget", icon=icon2, tooltip="组件", panel=self.panel())

        icon3 = QIcon()
        icon3.addPixmap(iconPack.toPixmap("ic_fluent_window_edit_regular"), QIcon.Mode.Normal, QIcon.State.Off)
        icon3.addPixmap(iconPack.toPixmap("ic_fluent_window_edit_filled"), QIcon.Mode.Normal, QIcon.State.On)
        self.addToggleButton(name="btnTest", icon=icon3, tooltip="测试", panel=self.panel())

        icon4 = QIcon()
        icon4.addPixmap(iconPack.toPixmap("ic_fluent_comment_multiple_regular"), QIcon.Mode.Normal, QIcon.State.Off)
        icon4.addPixmap(iconPack.toPixmap("ic_fluent_comment_multiple_filled"), QIcon.Mode.Normal, QIcon.State.On)
        self.addToggleButton(name="btnInfo", icon=icon4, tooltip="状态与信息", panel=self.panel())

        icon5 = QIcon()
        icon5.addPixmap(iconPack.toPixmap("ic_fluent_bug_regular"), QIcon.Mode.Normal, QIcon.State.Off)
        icon5.addPixmap(iconPack.toPixmap("ic_fluent_bug_filled"), QIcon.Mode.Normal, QIcon.State.On)
        self.addToggleButton(name="btnDebug", icon=icon5, tooltip="调试", panel=self.panel())

        icon6 = QIcon()
        icon6.addPixmap(iconPack.toPixmap("ic_fluent_info_regular"), QIcon.Mode.Normal, QIcon.State.Off)
        icon6.addPixmap(iconPack.toPixmap("ic_fluent_info_filled"), QIcon.Mode.Normal, QIcon.State.On)
        self.addToggleButton(name="btnAbout", icon=icon6, tooltip="关于", panel=self.panel())

        icon7 = QIcon()
        icon7.addPixmap(iconPack.toPixmap("ic_fluent_settings_regular"), QIcon.Mode.Normal, QIcon.State.Off)
        icon7.addPixmap(iconPack.toPixmap("ic_fluent_settings_filled"), QIcon.Mode.Normal, QIcon.State.On)
        self.addToggleButton(name="btnSettings", icon=icon7, tooltip="设置", panel=self.footerPanel())
