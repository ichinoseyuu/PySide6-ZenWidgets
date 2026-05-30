from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout,QSizePolicy
from PySide6.QtCore import Qt, QMargins,QPoint,QSize
from PySide6.QtGui import QFont, QIcon, QColor
from ZenWidgets import *

class PanelInfo(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelInfo')
        self.setLayout(ZVBoxLayout(self, QMargins(40, 30, 40, 30), 30, Qt.AlignmentFlag.AlignTop))
        self._setup_ui()


    def _setup_ui(self):
        self.title = ZHeadLine(self, text='状态与信息', display_indicator=True)
        self.title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))
        self.title.setPadding(ZPadding(6, 0, 6, 6))
        self.layout().addWidget(self.title)
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        card = ZCard(self)
        self.layout().addWidget(card)

        title = ZHeadLine(self, text='ZToolTip')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)
        card.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        vcontainer = ZVContainer(self)

        hcontainer_1 = ZHContainer(card)

        self.headline_1 = ZHeadLine(hcontainer_1, text='显示文字：')
        hcontainer_1.addWidget(self.headline_1)

        self.lineedit = ZLineEdit(hcontainer_1, text='这是一个工具提示窗口')
        hcontainer_1.addWidget(self.lineedit)

        hcontainer_2 = ZHContainer(card)

        self.headline_2 = ZHeadLine(hcontainer_2, text='显示位置：')
        hcontainer_2.addWidget(self.headline_2)

        self.combobox_1 = ZComboBox(self)
        for pos in ZPosition:
            if pos == ZPosition.Center: break
            self.combobox_1.addOption(pos.name, pos)
        self.combobox_1.toggleTo(ZPosition.TopRight.name)
        hcontainer_2.addWidget(self.combobox_1)

        self.headline_3 = ZHeadLine(hcontainer_2, text='跟随目标：')
        hcontainer_2.addWidget(self.headline_3)

        self.combobox_2 = ZComboBox(self)
        for mode in ZToolTip.Mode:
            self.combobox_2.addOption(mode.name, mode)
        self.combobox_2.toggleTo(ZToolTip.Mode.TrackMouse.name)
        hcontainer_2.addWidget(self.combobox_2)

        hcontainer_3 = ZHContainer(card)

        self.headline_4 = ZHeadLine(hcontainer_3, text='隐藏时间：')
        hcontainer_3.addWidget(self.headline_4)

        self.numberedit_1 = ZNumberEdit(hcontainer_3,integer_digits=4,step=500,minimumSize=QSize(100, 30))
        hcontainer_3.addWidget(self.numberedit_1)

        self.headline_5 = ZHeadLine(hcontainer_3, text='位置偏移：')
        hcontainer_3.addWidget(self.headline_5)

        self.numberedit_2 = ZNumberEdit(hcontainer_3,text='6',integer_digits=2,step=1,allow_negative=True,minimumSize=QSize(100, 30))
        hcontainer_3.addWidget(self.numberedit_2)

        self.numberedit_3 = ZNumberEdit(hcontainer_3,text='6',integer_digits=2,step=1,allow_negative=True,minimumSize=QSize(100, 30))
        hcontainer_3.addWidget(self.numberedit_3)

        hcontainer_4 = ZHContainer(card)
        hcontainer_4.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.panel_1 = ZPanel(hcontainer_4)
        self.panel_1.setFixedSize(100, 100)
        hcontainer_4.addWidget(self.panel_1)

        self.panel_2 = ZPanel(hcontainer_4)
        self.panel_2.setFixedSize(100, 100)
        hcontainer_4.addWidget(self.panel_2,spacing=60)

        self.panel_3 = ZPanel(hcontainer_4)
        self.panel_3.setFixedSize(100, 100)
        hcontainer_4.addWidget(self.panel_3,spacing=60)

        vcontainer.addWidget(hcontainer_1)
        vcontainer.addWidget(hcontainer_2)
        vcontainer.addWidget(hcontainer_3)
        vcontainer.addWidget(hcontainer_4)

        self.panel_1.enterEvent = self._on_target_enter
        self.panel_1.leaveEvent = self._on_target_leave
        self.panel_2.enterEvent = self._on_target_enter
        self.panel_2.leaveEvent = self._on_target_leave
        self.panel_3.enterEvent = self._on_target_enter
        self.panel_3.leaveEvent = self._on_target_leave
        card.layout().addWidget(vcontainer)


    def _on_target_enter(self, event):
        # 从控件获取当前设置
        position = self.combobox_1.currentValue()
        mode = self.combobox_2.currentValue()
        hide_delay = self.numberedit_1.value()
        offset = QPoint(self.numberedit_2.value(), self.numberedit_3.value())
        text = self.lineedit.text()
        if self.panel_1.underMouse():
            ZGlobal.tooltip.showTip(
                text=text,
                target=self.panel_1,
                mode=mode,
                position=position,
                offset=offset,
                hide_delay=hide_delay
            )
        elif self.panel_2.underMouse():
            ZGlobal.tooltip.showTip(
                text=text,
                target=self.panel_2,
                mode=mode,
                position=position,
                offset=offset,
                hide_delay=hide_delay
            )
        elif self.panel_3.underMouse():
            ZGlobal.tooltip.showTip(
                text=text,
                target=self.panel_3,
                mode=mode,
                position=position,
                offset=offset,
                hide_delay=hide_delay
            )

    def _on_target_leave(self, event):
        # 鼠标离开，立即隐藏工具提示
        ZGlobal.tooltip.hideTip()
