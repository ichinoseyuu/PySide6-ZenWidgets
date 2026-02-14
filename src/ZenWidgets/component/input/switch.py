from PySide6.QtWidgets import QSizePolicy
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QRectF, QPointF
from ZenWidgets.component.base import (
    ZAnimatedColor,
    ZAnimatedOpacity,
    ZAnimatedFloat,
    ZColorController,
    ZWidget,
    ZToggleWidget
)
from ZenWidgets.core import ZDebug
from ZenWidgets.gui import (
    ZSwitchStyle,
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

# region SwitchHandle
class SwitchHandle(ZWidget):
    bodyCtrl: ZAnimatedColor
    scaleCtrl: ZAnimatedFloat
    def __init__(self, parent: ZWidget | None = None):
        super().__init__(parent)
        self.scale_nomal = 0.85
        self.scale_hover = 1.0
        self.scaleCtrl.setValue(self.scale_nomal)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center = QPointF(self.width()/2, self.height()/2)
        radius = self.height()/2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.bodyCtrl.color)
        scaled_radius = radius * self.scaleCtrl.value
        painter.drawEllipse(center, scaled_radius, scaled_radius)
        event.accept()

class ZSwitchColorData(ZColorData):
    Body: QColor
    Border: QColor
    Handle: QColor
    HandleToggled: QColor

colordata = {
    'Light': {
        ZColorDataKey.Body: lambda: ZPalette.Primary,
        ZColorDataKey.Border: lambda: ZPalette.BorderNeutral,
        ZColorDataKey.Handle: lambda: ZPalette.SwitchHandle,
        ZColorDataKey.HandleToggled: ZPalette.White
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.Primary,
        ZColorDataKey.Border: lambda: ZPalette.BorderNeutral,
        ZColorDataKey.Handle: lambda: ZPalette.SwitchHandle,
        ZColorDataKey.HandleToggled: ZPalette.Black_78
    }
}
# region ZSwitch
@colordata_provider(datamap=colordata, classtype=ZSwitchColorData)
class ZSwitch(ZToggleWidget[ZSwitchStyle]):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    opacityCtrl: ZAnimatedOpacity
    colorDataCtrl: ZColorController[ZSwitchColorData]
    __controllers_kwargs__ = {'colorDataCtrl':{'key': 'ZSwitch'}}
    def __init__(self,
                 parent: ZWidget | None = None,
                 tun_on: bool = False,
                 style: ZSwitchStyle = ZSwitchStyle.Standard,
                 objectName: str | None = None,
                 ):
        super().__init__(parent,
                         checked=tun_on,
                         style=style,
                         objectName=objectName,
                         sizePolicy=QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                         )
        self._handle = SwitchHandle(self)
        self._init_color_data_()
        self._init_style_()

    # private method
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColor(data.Body)
        self._handle.bodyCtrl.color = data.HandleToggled
        if not self._checked:
            self.bodyColorCtrl.transparent()
            self._handle.bodyCtrl.color = data.Handle
        self.borderColorCtrl.color = data.Border

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        if self._checked:
            self.bodyColorCtrl.setColorTo(data.Body)
            self._handle.bodyCtrl.setColorTo(data.HandleToggled)
        else:
            self.bodyColorCtrl.setColor(data.Body)
            self.bodyColorCtrl.transparent()
            self._handle.bodyCtrl.setColorTo(data.Handle)
        self.borderColorCtrl.setColorTo(data.Border)

    def _init_style_(self):
        style = self._style.value
        self.setFixedSize(style.Width, style.Height)
        self._handle.setFixedSize(style.HandleDiameter, style.HandleDiameter)
        self._handle.move(style.Margin, style.Margin)

    def _update_style_(self):
        style = self._style.value
        self.setFixedSize(style.Width, style.Height)
        self._handle.setFixedSize(style.HandleDiameter, style.HandleDiameter)
        self._handle.move(style.Margin, style.Margin)

    def _mouse_enter_(self): self._handle.scaleCtrl.setValueTo(self._handle.scale_hover)

    def _mouse_leave_(self): self._handle.scaleCtrl.setValueTo(self._handle.scale_nomal)

    def _toggle_(self):
        data = self.colorDataCtrl.data
        if self._checked:
            self.bodyColorCtrl.toOpaque()
            self._handle.bodyCtrl.setColorTo(data.HandleToggled)
        else:
            self.bodyColorCtrl.toTransparent()
            self._handle.bodyCtrl.setColorTo(data.Handle)
        handle_width = self._handle.width()
        margin = self._style.value.Margin
        target_x = self.width() - handle_width - margin if self._checked else margin
        target_y = margin
        self._handle.widgetPositionCtrl.moveTo(target_x, target_y)

    # public method
    def isTurnOn(self) -> bool: return self._checked

    # event
    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        radius = self.height()/2
        if self._checked:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.bodyColorCtrl.color)
            painter.drawRoundedRect(rect, radius, radius)
        else:
            painter.setPen(QPen(self.borderColorCtrl.color, 1))
            painter.setBrush(self.bodyColorCtrl.color)
            painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()

