from PySide6.QtWidgets import QWidget,QSizePolicy
from PySide6.QtCore import Qt,QRectF,QMargins
from PySide6.QtGui import QPainter,QPen,QPainterPath,QColor
from ZenWidgets.component.base import ZAnimatedColor,ZAnimatedFloat,ZColorController,ZWidget
from ZenWidgets.component.layouts import ZVBoxLayout,ZHBoxLayout
from ZenWidgets.core import ZDebug
from ZenWidgets.gui import (
    ZWidgetEffect,
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

class ZCardColorData(ZColorData):
    Body: QColor
    Border: QColor
    Underline: QColor

colordata = {
    'Light':  {
        ZColorDataKey.Body: lambda: ZPalette.CardBody,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Underline: lambda: ZPalette.Underline
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.CardBody,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Underline: lambda: ZPalette.Underline
    }
}

@colordata_provider(datamap=colordata, classtype=ZCardColorData)
class ZCard(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    underlineColorCtrl: ZAnimatedColor
    underlineWeightCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZCardColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZCard'},
        'radiusCtrl': {'value': 8.0},
        'underlineWeightCtrl': {'value': 1.5},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 display_border: bool = True,
                 display_underline: bool = True,
                 display_shadow: bool = False,
                 objectName: str | None = None,
                 sizePolicy: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         sizePolicy=sizePolicy
                         )
        self._display_border = display_border
        self._display_underline = display_underline
        self._display_shadow = display_shadow
        self._init_color_data_()
        self.setLayout(ZVBoxLayout(self,margins=QMargins(16,16,16,16),spacing=16))
        if self._display_shadow: ZWidgetEffect.applyGraphicsShadow(self)

    def setShadowDisplay(self, display: bool,/):
        self._display_shadow = display
        self.update()

    def setBorderDisplay(self, display: bool,/):
        self._display_border = display
        self.update()

    def sizeHint(self): return self.layout().sizeHint()

    # region private
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border
        self.underlineColorCtrl.color = data.Underline

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)
        self.underlineColorCtrl.setColorTo(data.Underline)

    # region event
    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value
        clip = QPainterPath()
        clip.addRoundedRect(rect, radius, radius)

        painter.setClipPath(clip)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, self.bodyColorCtrl.color)


        if self._display_border:
            painter.setPen(QPen(self.borderColorCtrl.color, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        if self._display_underline:
            shadow_w = self.underlineWeightCtrl.value
            painter.fillRect(QRectF(rect.left(), rect.bottom() - shadow_w, rect.width(), shadow_w),
                             self.underlineColorCtrl.color)

        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()

