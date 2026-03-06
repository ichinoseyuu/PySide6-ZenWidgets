from PySide6.QtCore import Qt,Signal,QMargins,QSize,QTimer
from PySide6.QtGui import QFont,QPainter,QPen,QColor
from PySide6.QtWidgets import QSizePolicy
from ZenWidgets.component.layouts import ZHBoxLayout
from ZenWidgets.component.base import (
    ZClickWidget,
    ZWidget,
    ZColorController,
    ZAnimatedColor,
    ZAnimatedFloat,
    ZOpacityEffect,
)
from ZenWidgets.core import ZPadding
from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

class ZMenubarItemColorData(ZColorData):
    Text: QColor

colordata = {
    'Light': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
    },
    'Dark': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
    }
}

@colordata_provider(datamap=colordata, classtype=ZMenubarItemColorData)
class ZMenubarItem(ZClickWidget):
    triggered = Signal()
    textColorCtrl: ZAnimatedColor
    opacityEffectCtrl: ZOpacityEffect
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZMenubarItemColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl': {'key': 'ZMenubarItem'},
        'radiusCtrl': {'value': 4.0},
    }
    def __init__(self,
                 text: str,
                 parent=None,
                 font=QFont("Microsoft YaHei", 10)
                 ):
        super().__init__(
            parent=parent,
            font=font,
            sizePolicy=QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed),
            focusPolicy=Qt.FocusPolicy.TabFocus
        )
        self._text = text
        self._padding = ZPadding(8, 4, 8, 4)
        self.setFixedHeight(28)
        self._menu = None
        self._init_color_data_()

    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.setColorTo(data.Text)

    def _mouse_enter_(self): self.opacityEffectCtrl.setAlphaFTo(0.11)
    def _mouse_leave_(self): self.opacityEffectCtrl.toTransparent()
    def _mouse_press_(self): self.opacityEffectCtrl.setAlphaFTo(0.16)
    def _mouse_release_(self): self.opacityEffectCtrl.setAlphaFTo(0.11)

    def setText(self, t: str):
        if self._text == t: return
        self._text = t
        self.update()

    def text(self) -> str:
        return self._text

    def setMenu(self, menu):
        self._menu = menu

    def sizeHint(self):
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text)
        width = text_width + self._padding.left + self._padding.right
        height = fm.height() + self._padding.top + self._padding.bottom
        return QSize(width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing|
            QPainter.RenderHint.TextAntialiasing|
            QPainter.RenderHint.SmoothPixmapTransform
            )
        rect = self.rect()
        radius = self.radiusCtrl.value
        self.opacityEffectCtrl.drawOpacityLayer(painter, rect, radius)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(rect)
        painter.setPen(QPen(self.textColorCtrl.color))
        painter.setFont(self.font())
        text_rect = rect.adjusted(self._padding.left, self._padding.top, -self._padding.right, -self._padding.bottom)
        painter.drawText(text_rect, Qt.AlignCenter, self._text)
        event.accept()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self._menu: QTimer.singleShot(0, lambda: self._menu.showAt(self.mapToGlobal(self.rect().bottomLeft())))

class ZMenubar(ZWidget):
    menuTriggered = Signal(str, object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(ZHBoxLayout(self, margins=QMargins(6, 2, 6, 2), spacing=6, alignment=Qt.AlignLeft))
        self._items = []

    def addMenu(self, text: str, menu=None):
        item = ZMenubarItem(text, self)
        self.layout().addWidget(item)
        self._items.append(item)
        if menu:
            item.setMenu(menu)
            menu.itemSelected.connect(lambda t, v: self.menuTriggered.emit(t, v))