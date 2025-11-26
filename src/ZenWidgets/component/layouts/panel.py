from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QPainter,QPen
from ZenWidgets.component.base import ZAnimatedColor,ZAnimatedFloat,ZColorController,ZWidget
from ZenWidgets.core import ZDebug
from ZenWidgets.gui import ZPanelColorData

class ZPanel(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZPanelColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZPanel'},
        'radiusCtrl': {'value': 5.0},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 objectName: str | None = None,
                 ):
        super().__init__(parent=parent, objectName=objectName)
        self._init_color_data_()

    # region private
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)

    # region event
    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        border_rect = QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = self.radiusCtrl.value

        if self.bodyColorCtrl.color.alpha() > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.bodyColorCtrl.color)
            painter.drawRoundedRect(rect, radius, radius)

        if self.borderColorCtrl.color.alpha() > 0:
            painter.setPen(QPen(self.borderColorCtrl.color, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(border_rect, radius, radius)

        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()

