import logging
from enum import IntEnum, auto
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt,QRectF,QSize,QPoint,QTimer,QElapsedTimer
from PySide6.QtGui import QFont,QFontMetrics,QPainter,QPen,QCursor,QColor
from ZenWidgets.component.base import (
    ZFlashEffect,
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController,
    ZWidget
)
from ZenWidgets.core import ZDebug,ZPosition,ZPadding,ZMargins
from ZenWidgets.gui import (
    ZWidgetEffect,
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)
class ZToolTipColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor

colordata = {
    'Light':  {
        ZColorDataKey.Body: lambda: ZPalette.PanelBody,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Text: lambda: ZPalette.Text
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.PanelBody,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Text: lambda: ZPalette.Text
    }
}
# region ZToolTip
@colordata_provider(datamap=colordata, classtype=ZToolTipColorData)
class ZToolTip(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    flashCtrl: ZFlashEffect
    textColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[ZToolTipColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl': {'key': 'ZToolTip'},
        'radiusCtrl': {'value': 4.0},
        }

    class Mode(IntEnum):
        TrackMouse = auto()
        TrackTarget = auto()

    def __init__(self):
        super().__init__(
            f=Qt.WindowType.FramelessWindowHint|
            Qt.WindowType.WindowStaysOnTopHint|
            Qt.WindowType.WindowTransparentForInput|
            Qt.WindowType.Tool,
            maximumWidth=316,
            minimumHeight=44,
            font=QFont("Microsoft YaHei", 9),
            height_for_width=True
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._full_text: str = ""
        self._display_text: str = ""
        self._margin = ZMargins(8, 8, 8, 8)
        self._padding = ZPadding(10, 8, 10, 8)
        self._alignment = Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter


        self._target: QWidget | None = None
        self._mode = self.Mode.TrackMouse
        self._position = ZPosition.Top
        self._offset = QPoint(0, 0)

        self._show_cd = 33
        self._cd_timer = QElapsedTimer()

        self._tracker_timer = QTimer()
        self._tracker_timer.setInterval(int(1000/60))
        self._tracker_timer.timeout.connect(self._update_pos_for_tracker)

        self._show_timer = QTimer(singleShot=True, interval=1000)
        self._hide_timer = QTimer(singleShot=True)
        self._hide_timer.timeout.connect(self.hideTip)

        self.windowOpacityCtrl.animation.init(factor=0.2, bias=0.02, current_value=0)
        self.windowOpacityCtrl.completelyHide.connect(self.hide)

        self.widgetSizeCtrl.animation.init(factor=0.15, bias=1)
        self.widgetPositionCtrl.animation.init(factor=0.1, bias=1)
        self._init_color_data_()
        self.resize(self.sizeHint())

    # region private
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.setColorTo(data.Text)
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)

    def _update_pos_for_tracker(self):
        self.widgetPositionCtrl.moveFromTo(self.pos(), self._get_pos_should_be_move())

    def _get_initial_pos(self):
        tip_pos = self._position
        w, h  = self.width(), self.height()
        shadow = self._margin.left
        offset = self._offset
        if self._mode == self.Mode.TrackMouse:
            m = QCursor.pos()
            cw, ch = self.width()- self._margin.horizontal(), self.height()- self._margin.vertical()

            if tip_pos == ZPosition.Top:
                return QPoint(m.x() - w//2, m.y() - ch - shadow - offset.y())

            if tip_pos == ZPosition.Bottom:
                return QPoint(m.x() - w//2, m.y() - shadow + offset.y())

            if tip_pos == ZPosition.Left:
                return QPoint(m.x() - cw - shadow - offset.x(), m.y() - h//2)

            if tip_pos == ZPosition.Right:
                return QPoint(m.x() - shadow + offset.x(), m.y() - h//2)

            if tip_pos == ZPosition.TopLeft:
                return QPoint(m.x() - cw - shadow - offset.x(), m.y() - ch - shadow - offset.y())

            if tip_pos == ZPosition.TopRight:
                return QPoint(m.x() - shadow + offset.x(), m.y() - ch - shadow - offset.y())

            if tip_pos == ZPosition.BottomLeft:
                return QPoint(m.x() - cw - shadow - offset.x(), m.y() - shadow + offset.y())

            if tip_pos == ZPosition.BottomRight:
                return QPoint(m.x() - shadow + offset.x(), m.y() - shadow + offset.y())

        if self._mode == self.Mode.TrackTarget:
            tc = self._target.mapToGlobal(self._target.rect().center())
            if tip_pos == ZPosition.Top:
                return tc - QPoint(w//2, h)

            elif tip_pos == ZPosition.Bottom:
                return tc - QPoint(w//2, 0)

            elif tip_pos == ZPosition.Left:
                return tc - QPoint(w, h//2)

            elif tip_pos == ZPosition.Right:
                return tc - QPoint(0, h//2)

            elif tip_pos == ZPosition.TopLeft:
                return tc - QPoint(w, h)

            elif tip_pos == ZPosition.TopRight:
                return tc - QPoint(0, h)

            elif tip_pos == ZPosition.BottomLeft:
                return tc - QPoint(w, 0)

            elif tip_pos == ZPosition.BottomRight:
                return tc

    def _get_pos_should_be_move(self) -> QPoint:
        m = QCursor.pos()

        if self._target is None: return m

        # condition
        mode = self._mode
        tip_pos = self._position

        # target
        tc = self._target.mapToGlobal(self._target.rect().center())
        tw, th = self._target.width(), self._target.height()
        tt, tl, tb, tr = tc.y() - th//2, tc.x() - tw//2, tc.y() + th//2, tc.x() + tw//2

        # self
        w, h  = self.width(), self.height()
        cw, ch = self.width()- self._margin.horizontal(), self.height()- self._margin.vertical()
        shadow = self._margin.left
        offset = self._offset

        if mode == self.Mode.TrackMouse:
            if tip_pos == ZPosition.Top:
                return QPoint(m.x() - w//2, m.y() - ch - shadow - offset.y())

            if tip_pos == ZPosition.Bottom:
                return QPoint(m.x() - w//2, m.y() - shadow + offset.y())

            if tip_pos == ZPosition.Left:
                return QPoint(m.x() - cw - shadow - offset.x(), m.y() - h//2)

            if tip_pos == ZPosition.Right:
                return QPoint(m.x() - shadow + offset.x(), m.y() - h//2)

            if tip_pos == ZPosition.TopLeft:
                return QPoint(m.x() - cw - shadow - offset.x(), m.y() - ch - shadow - offset.y())

            if tip_pos == ZPosition.TopRight:
                return QPoint(m.x() - shadow + offset.x(), m.y() - ch - shadow - offset.y())

            if tip_pos == ZPosition.BottomLeft:
                return QPoint(m.x() - cw - shadow - offset.x(), m.y() - shadow + offset.y())

            if tip_pos == ZPosition.BottomRight:
                return QPoint(m.x() - shadow + offset.x(), m.y() - shadow + offset.y())

        if mode == self.Mode.TrackTarget:
            if tip_pos == ZPosition.Top:
                return QPoint(tc.x() - w//2, tt - ch - shadow - offset.y())

            if tip_pos == ZPosition.Bottom:
                return QPoint(tc.x() - w//2, tb + offset.y() - shadow)

            if tip_pos == ZPosition.Left:
                return QPoint(tl - cw - shadow - offset.x(), tc.y() - h//2)

            if tip_pos == ZPosition.Right:
                return QPoint(tr - shadow + offset.x(), tc.y() - h//2)

            if tip_pos == ZPosition.TopLeft:
                return QPoint(tl - cw - shadow - offset.x(), tt - ch - shadow - offset.y())

            if tip_pos == ZPosition.TopRight:
                return QPoint(tr - shadow + offset.x(), tt - ch - shadow - offset.y())

            if tip_pos == ZPosition.BottomLeft:
                return QPoint(tl - cw - shadow - offset.x(), tb - shadow + offset.y())

            if tip_pos == ZPosition.BottomRight:
                return QPoint(tr - shadow + offset.x(), tb - shadow + offset.y())


    # region public
    def mode(self) -> Mode: return self._mode

    def position(self) -> ZPosition: return self._position

    def offset(self) -> QPoint: return self._offset

    def text(self) -> str: return self._full_text

    def target(self): return self._target

    def setText(self, t: str,/,flash: bool = False) -> None:
        if flash or self._full_text != t: self.flashCtrl.flash(0.3)
        self._full_text = t
        #self.resize(self.sizeHint())
        self.widgetSizeCtrl.resizeFromTo(self.size(), self.sizeHint())
        self.update()

    def showTip(self,
                text: str,
                target: QWidget,
                mode: Mode = Mode.TrackMouse,
                position: ZPosition = ZPosition.Top,
                offset: QPoint = QPoint(0, 0),
                hide_delay: int = 0,
                flash: bool = False):
        if self._cd_timer.isValid() and self._cd_timer.elapsed() < self._show_cd: return
        if self._hide_timer.isActive(): self._hide_timer.stop()
        self.setText(text, flash)
        self._target = target
        self._mode = mode
        self._offset = offset
        self._position = position
        if self.windowOpacity() == 0:
            self.widgetSizeCtrl.resizeFromTo(self.minimumSize(), self.sizeHint())
            self.move(self._get_initial_pos())
            self._tracker_timer.start()
            self.windowOpacityCtrl.fadeIn()
        else:
            new_pos = self._get_pos_should_be_move()
            if (new_pos - self.pos()).manhattanLength() > 200:
                self.widgetSizeCtrl.resizeFromTo(self.minimumSize(), self.sizeHint())
                self.move(self._get_initial_pos())
                self._tracker_timer.start()
                self.windowOpacityCtrl.fadeTo(.0, 1.0)
            else:
                self.widgetSizeCtrl.resizeFromTo(self.size(), self.sizeHint())
                self.widgetPositionCtrl.moveFromTo(self.pos(), new_pos)
                self._tracker_timer.start()
                self.windowOpacityCtrl.fadeTo(1.0)
        if flash: self.flashCtrl.flash(0.3)
        self.raise_()
        self.show()
        if hide_delay > 0: self._hide_timer.start(hide_delay)
        self._cd_timer.start()

    def hideTip(self):
        self.windowOpacityCtrl.fadeOut()
        self._target = None
        if self._tracker_timer.isActive():self._tracker_timer.stop()

    def hideTipDelayed(self, delay: int):
        if self._hide_timer.isActive(): self._hide_timer.stop()
        self._hide_timer.start(delay)

    def adjustSize(self): self.resize(self.sizeHint())

    def heightForWidth(self, width: int) -> int:
        p = self._padding
        if not self._full_text: return max(p.vertical(), 28)
        fm = QFontMetrics(self.font())
        rect = fm.boundingRect(
            0, 0, width, 0,
            Qt.TextFlag.TextWrapAnywhere | self._alignment,
            self._full_text
            )
        height = max(rect.height() + p.vertical(), 28)
        return height

    def sizeHint(self):
        p = self._padding
        if not self._full_text: return QSize(p.horizontal(), 28)
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self._full_text) + p.horizontal() + 1
        if text_width <= self.minimumWidth():
            width = self.minimumWidth()
        elif text_width <= self.maximumWidth():
            width = text_width
        else:
            width = self.maximumWidth()
        height = self.heightForWidth(width)
        return QSize(width, height)+QSize(self._margin.horizontal(),self._margin.vertical())

    # region event
    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing|QPainter.RenderHint.TextAntialiasing)
        m = self._margin
        rect = QRectF(self.rect()).adjusted(m.left, m.top, -m.right, -m.bottom)
        radius = self.radiusCtrl.value

        ZWidgetEffect.drawGraphicsShadow(painter, rect, radius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5),radius, radius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.flashCtrl.color)
        painter.drawRoundedRect(rect, radius, radius)

        painter.setFont(self.font())
        painter.setPen(self.textColorCtrl.color)
        p = self._padding

        text_rect = QRectF(
            rect.left() + p.left,
            rect.top() + p.top,
            self.maximumWidth()-m.horizontal()-p.horizontal(),
            rect.height() - p.vertical()
        )
        #text_rect = rect.adjusted(p.left, p.top, -p.right, -p.bottom)
        painter.drawText(text_rect,self._alignment|Qt.TextFlag.TextWrapAnywhere,self._full_text)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()