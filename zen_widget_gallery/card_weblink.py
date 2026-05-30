from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets import *
from ZenWidgets.component.media import ZImage
from ZenWidgets.component.text import ZHeadLine, ZTextBlock

class CardWebLinkColorData(ZColorData):
    Body: QColor
    Border: QColor

colordata = {
    'Light': {
        ZColorDataKey.Body: lambda: ZPalette.Body,
        ZColorDataKey.Border: lambda: ZPalette.BorderEmphasized
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.Body,
        ZColorDataKey.Border: lambda: ZPalette.BorderEmphasized
    }
}

@colordata_provider(datamap=colordata, classtype=CardWebLinkColorData)
class CardWebLink(ZClickWidget[ZButtonStyle]):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[CardWebLinkColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'CardWebLink'}
    }

    def __init__(self,
                 parent: QWidget | None = None,
                 title: str = "",
                 description: str = "",
                 icon: str = "",
                 font: QFont = QFont('Microsoft YaHei', 8)
                 ):
        super().__init__(parent=parent, font=font)
        self._icon = ZImage(self)
        if icon:
            self._icon.setImage(icon)
        self._icon.setFixedSize(48, 48)
        self._title = ZHeadLine(self, text=title, font=QFont('Microsoft YaHei', 9, QFont.Weight.Bold))
        self._desc = ZTextBlock(self, text=description, font=QFont('Microsoft YaHei', 8), height_for_width=True)

        self._icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._title.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._desc.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout = ZVBoxLayout(self, margins=QMargins(16, 16, 16, 16), spacing=8)
        layout.addWidget(self._icon)
        layout.addWidget(self._title)
        layout.addWidget(self._desc)
        self.setLayout(layout)
        self.setFixedSize(230, 170)
        self._init_color_data_()

    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.borderColorCtrl.color = data.Border
        self.borderColorCtrl.setAlphaF(0.6)
        self.bodyColorCtrl.setColor(data.Body)
        self.bodyColorCtrl.setAlphaF(0.8)

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.borderColorCtrl.color = data.Border
        self.borderColorCtrl.setAlphaFTo(0.6)
        self.bodyColorCtrl.setColor(data.Body)
        self.bodyColorCtrl.setAlphaFTo(0.8)

    def _mouse_enter_(self):
        self.borderColorCtrl.toOpaque()
        self.bodyColorCtrl.setAlphaFTo(0.9)
        self.update()

    def _mouse_leave_(self):
        self.borderColorCtrl.setAlphaFTo(0.6)
        self.bodyColorCtrl.setAlphaFTo(0.8)
        self.update()

    def _mouse_click_(self):
        pass

    def setTarget(self, target):
        self._target = target

    def setCallback(self, cb):
        self._callback = cb

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )

        rect = QRectF(self.rect()).adjusted(.5, .5, -.5, -.5)
        radius = 8
        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(rect, radius, radius)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._mouse_enter_()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._mouse_leave_()