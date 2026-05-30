from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from ZenWidgets.component.base import (
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController,
    ZWidget
)
from ZenWidgets.core import (
    ZExpPropertyAnimation,
    ZDirection,
    ZState
)
from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

# region ZScrollHandle
class ZScrollHandleColorData(ZColorData):
    Body: QColor

scrollhandle_colordata = {
    'Light': {
        ZColorDataKey.Body: lambda: ZPalette.ScrollHandle
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.ScrollHandle
    }
}

@colordata_provider(datamap=scrollhandle_colordata, classtype=ZScrollHandleColorData)
class ZScrollHandle(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZScrollHandleColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl': {'key': 'ZScrollHandle'}
    }

    def __init__(self, parent: ZWidget|None = None, direction = ZDirection.Vertical):
        super().__init__(parent)
        if direction not in (ZDirection.Horizontal, ZDirection.Vertical): raise ValueError('Invalid direction')
        self._dir: ZDirection = direction
        self._is_scroll_dragging: bool = False
        self._scroll_drag_start_pos: QPoint = QPoint()
        self._handle_width: int = 2
        self._handle_width_min: int = 2
        self._handle_width_max: int = 6
        self._length_anim = ZExpPropertyAnimation(self, "handleLength")
        self._width_anim = ZExpPropertyAnimation(self, "handleWidth")
        self._width_anim.setBias(0.5)
        self._width_anim.setFactor(0.2)
        self._trans_timer = QTimer(self)
        self._trans_timer.setSingleShot(True)
        self._trans_timer.timeout.connect(self.toTransparent)
        if self._dir == ZDirection.Vertical:
            self.setFixedWidth(self._handle_width_max)
        else:
            self.setFixedHeight(self._handle_width_max)
        self.radiusCtrl.value = self._handle_width / 2
        self._init_color_data_()

    def _init_color_data_(self):
        self.bodyColorCtrl.color = self.colorDataCtrl.data.Body

    def _color_data_change_handler_(self):
        self.bodyColorCtrl.setColorTo(self.colorDataCtrl.data.Body)
        self._trans_timer.start(1200)

    # region property
    def getHandleLength(self): return self.height() if self._dir == ZDirection.Vertical else self.width()

    def setHandleLength(self, value):
        self.setFixedHeight(value) if self._dir == ZDirection.Vertical else self.setFixedWidth(value)

    handleLength: int = Property(int, getHandleLength, setHandleLength)

    def getHandleWidth(self): return self._handle_width

    def setHandleWidth(self, value):
        self._handle_width = value
        self.radiusCtrl.value = value / 2
        self.update()

    handleWidth: int = Property(int, getHandleWidth, setHandleWidth)

    # region public
    def setHandleLengthTo(self, value):
        self._length_anim.stop()
        self._length_anim.setStartValue(self.handleLength)
        self._length_anim.setEndValue(value)
        self._length_anim.start()

    def setHandleWidthTo(self, value):
        self._width_anim.stop()
        self._width_anim.setStartValue(self.handleWidth)
        self._width_anim.setEndValue(value)
        self._width_anim.start()

    def toTransparent(self):
        self.bodyColorCtrl.toTransparent()
        self._trans_timer.stop()

    def transparent(self):
        self.bodyColorCtrl.transparent()
        self._trans_timer.stop()

    def toOpaque(self):
        self.bodyColorCtrl.toOpaque()
        self._trans_timer.start(1200)

    def opaque(self):
        self.bodyColorCtrl.opaque()
        self._trans_timer.start(1200)

    # region event
    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())
        if self._dir == ZDirection.Vertical:
            rect = QRectF(self.width()-self._handle_width +.5, 3, self._handle_width-1, self.height()-3)
        else:
            rect = QRectF(3, self.height()-self._handle_width+.5, self.width()-3, self._handle_width-1)
        radius = self.radiusCtrl.value
        if self._state == ZState.Idle:
            painter.setPen(QPen(self.bodyColorCtrl.color, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect, radius, radius)
        elif self._state == ZState.Hover:
            painter.setPen(QPen(self.bodyColorCtrl.color, 1))
            painter.setBrush(self.bodyColorCtrl.color)
            painter.drawRoundedRect(rect, radius, radius)
        event.accept()

    def enterEvent(self, event):
        super().enterEvent(event)
        self._state = ZState.Hover
        self._trans_timer.stop()
        self.bodyColorCtrl.opaque()
        self.setHandleWidthTo(self._handle_width_max)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._state = ZState.Idle
        self.setHandleWidthTo(self._handle_width_min)
        self._trans_timer.start(1200)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_scroll_dragging = True
            self._scroll_drag_start_pos = event.globalPos() - self.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    # def mouseMoveEvent(self, event: QMouseEvent):
    #     if not self._is_scroll_dragging: return
    #     panel = self.parent()
    #     new_pos = event.globalPos() - self._scroll_drag_start_pos
    #     if self._dir == ZDirection.Vertical:
    #         y = max(0, min(new_pos.y(), panel.height() - panel._handle_h.height() - self.height()))
    #         percentage = y / (panel.height() - panel._handle_h.height() - self.height())
    #         max_scroll = panel._content.height() - panel.height()
    #         scroll_pos = int(percentage * max_scroll)
    #         panel.scrollTo(y=scroll_pos)
    #     else:
    #         x = max(0, min(new_pos.x(), panel.width() - panel._handle_v.width() - self.width()))
    #         percentage = x / (panel.width() - panel._handle_v.width() - self.width())
    #         max_scroll = panel._content.width() - panel.width()
    #         scroll_pos = int(percentage * max_scroll)
    #         panel.scrollTo(x=scroll_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_scroll_dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)


class ZScrollViewHandleV(ZScrollHandle):
    def __init__(self, parent: ZWidget|None = None):
        super().__init__(parent, direction = ZDirection.Vertical)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._is_scroll_dragging or self.opacityCtrl.opacity == 0: return
        panel = self.parent()
        new_pos = event.globalPos() - self._scroll_drag_start_pos
        y = max(0, min(new_pos.y(), panel.height() - panel._handle_h.height() - self.height()))
        percentage = y / (panel.height() - panel._handle_h.height() - self.height())
        max_scroll = panel._content.height() - panel.height()
        scroll_pos = int(percentage * max_scroll)
        panel.scrollTo(y=scroll_pos)


class ZScrollViewHandleH(ZScrollHandle):
    def __init__(self, parent: ZWidget|None = None):
        super().__init__(parent, direction = ZDirection.Horizontal)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._is_scroll_dragging or self.opacityCtrl.opacity == 0: return
        panel = self.parent()
        new_pos = event.globalPos() - self._scroll_drag_start_pos
        x = max(0, min(new_pos.x(), panel.width() - panel._handle_v.width() - self.width()))
        percentage = x / (panel.width() - panel._handle_v.width() - self.width())
        max_scroll = panel._content.width() - panel.width()
        scroll_pos = int(percentage * max_scroll)
        panel.scrollTo(x=scroll_pos)

class ZListViewHandleV(ZScrollHandle):
    def __init__(self, parent: ZWidget|None = None):
        super().__init__(parent, direction = ZDirection.Vertical)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._is_scroll_dragging or self.opacityCtrl.opacity == 0: return
        panel = self.parent()
        new_pos = event.globalPos() - self._scroll_drag_start_pos
        y = max(0, min(new_pos.y(), panel.height() - self.height()))
        percentage = y / (panel.height() - self.height())
        max_scroll = panel._content.height() - panel.height()
        scroll_pos = int(percentage * max_scroll)
        panel.scrollTo(y=scroll_pos)

class ZListViewHandleH(ZScrollHandle):
    def __init__(self, parent: ZWidget|None = None):
        super().__init__(parent, direction = ZDirection.Horizontal)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._is_scroll_dragging or self.opacityCtrl.opacity == 0: return
        panel = self.parent()
        new_pos = event.globalPos() - self._scroll_drag_start_pos
        x = max(0, min(new_pos.x(), panel.width() - self.width()))
        percentage = x / (panel.width() - self.width())
        max_scroll = panel._content.width() - panel.width()
        scroll_pos = int(percentage * max_scroll)
        panel.scrollTo(x=scroll_pos)