from PySide6.QtGui import QPainter,QFont,QPen,QIcon,QPixmap
from PySide6.QtCore import Qt,QRect,QSize,QRectF,QPoint
from PySide6.QtWidgets import QSizePolicy
from ZenWidgets.component.base import (
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController,
    ZOpacityEffect,
    LongPressTriggerWidget,
    ZWidget
    )
from ZenWidgets.core import (
    ZDebug,
    ZGlobal,
    ZPosition
)
from ZenWidgets.gui import ZLongPressButtonColorData

class ZLongPressButton(LongPressTriggerWidget):
    bodyColorCtrl: ZAnimatedColor
    progressColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    hoverLayerCtrl: ZOpacityEffect
    textColorCtrl: ZAnimatedColor
    iconColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[ZLongPressButtonColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZLongPressButton'},
        'radiusCtrl': {'value': 4.0},
        'progressCtrl': {'value': 0.0},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 text: str | None = None,
                 font: QFont = QFont('Microsoft YaHei', 9),
                 icon: QIcon | None = None,
                 icon_size: QSize = QSize(16, 16),
                 spacing: int = 4,
                 objectName: str | None = None,
                 toolTip: str | None = None,
                 sizePolicy: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         toolTip=toolTip,
                         font=font,
                         sizePolicy=sizePolicy
                         )
        self._text: str | None = text
        self._icon: QIcon | None = icon
        self._icon_size = icon_size
        self._spacing = spacing
        self._init_color_data_()
        self.resize(self.sizeHint())

    # region private method
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.progressColorCtrl.color = data.Progress
        self.textColorCtrl.color = data.Text
        self.iconColorCtrl.color = data.Icon
        self.borderColorCtrl.color = data.Border

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.progressColorCtrl.setColorTo(data.Progress)
        self.borderColorCtrl.setColorTo(data.Border)
        self.iconColorCtrl.setColorTo(data.Icon)
        self.textColorCtrl.setColorTo(data.Text)

    def _show_tooltip_(self):
        if self.toolTip() != '':
            ZGlobal.tooltip.showTip(
                text=self.toolTip(),
                target=self,
                position=ZPosition.TopRight,
                offset=QPoint(6, 6)
                )

    def _hide_tooltip_(self):
        if self.toolTip() != '': ZGlobal.tooltip.hideTip()

    def _mouse_enter_(self): self.hoverLayerCtrl.setAlphaFTo(0.06)

    def _mouse_leave_(self): self.hoverLayerCtrl.toTransparent()

    # region public method
    def text(self) -> str: return self._text

    def spacing(self) -> int: return self._spacing

    def icon(self) -> QIcon: return self._icon

    def iconSize(self) -> QSize: return self._icon_size

    def setText(self, t: str) -> None: self._text = t; self.update()

    def setIcon(self, i: QIcon) -> None: self._icon = i; self.update()

    def setIconSize(self, s: QSize) -> None: self._icon_size = s; self.update()

    def setSpacing(self, spacing: int) -> None: self._spacing = spacing; self.update()

    def sizeHint(self):
        if self._icon and not self._text:
            size = QSize(30, 30)
            self.setMinimumSize(size)
            return size
        elif not self._icon and self._text:
            size = QSize(self.fontMetrics().boundingRect(self._text).width() + 40, 30)
            self.setMinimumSize(size)
            return size
        else:
            size = QSize(self.fontMetrics().boundingRect(self._text).width() + 60, 30)
            self.setMinimumSize(size)
            return size

    # region event
    def enterEvent(self, event):
        super().enterEvent(event)
        self._show_tooltip_()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hide_tooltip_()

    def paintEvent(self, event) -> None:
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing|
            QPainter.RenderHint.TextAntialiasing|
            QPainter.RenderHint.SmoothPixmapTransform
            )
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value

        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        if self.progressCtrl.value > 0:
            progress_rect = rect.adjusted(1, 1, -1, -1)
            progress_rect.setWidth(progress_rect.width() * self.progressCtrl.value)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.progressColorCtrl.color)
            painter.drawRoundedRect(progress_rect, radius, radius)

        self.hoverLayerCtrl.drawOpacityLayer(painter, rect, radius)

        if self._icon:
            pixmap = self._icon.pixmap(self._icon_size)
            colored_pixmap = QPixmap(pixmap.size())
            colored_pixmap.setDevicePixelRatio(self.devicePixelRatioF())
            colored_pixmap.fill(Qt.transparent)
            with QPainter(colored_pixmap) as painter_pix:
                painter_pix.drawPixmap(0, 0, pixmap)
                painter_pix.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                painter_pix.fillRect(colored_pixmap.rect(), self.iconColorCtrl.color)
            if self._text:
                total_width = self._icon_size.width() + self._spacing + self.fontMetrics().boundingRect(self._text).width()
                start_x = (self.width() - total_width) / 2
                painter.drawPixmap(
                    start_x,
                    (self.height() - self._icon_size.height()) / 2,
                    colored_pixmap
                )
                painter.setFont(self.font())
                painter.setPen(self.textColorCtrl.color)
                painter.drawText(
                    QRect(start_x + self._icon_size.width() + self._spacing, 0, rect.width(), rect.height()),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    self._text
                )
            else:
                painter.drawPixmap(
                    (self.width() - self._icon_size.width()) / 2,
                    (self.height() - self._icon_size.height()) / 2,
                    colored_pixmap
                )
        elif self._text:
            painter.setFont(self.font())
            painter.setPen(self.textColorCtrl.color)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._text)

        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()