from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets.component.base import (
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController,
    ZWidget,
    ZContentWidget
)
from ZenWidgets.core import (
    ZGlobal,
    ZDebug,
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

# region ScrollHandle
class ScrollHandle(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat

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
        # init style
        self.radiusCtrl.value = self._handle_width / 2
        self.bodyColorCtrl.transparent()

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

    def parent(self) -> 'ZScrollPanel':
        return super().parent()

    # region event
    def paintEvent(self, event):
        painter = QPainter(self)
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

    # region mouseEvent
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_scroll_dragging = True
            self._scroll_drag_start_pos = event.globalPos() - self.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._is_scroll_dragging: return
        panel = self.parent()
        new_pos = event.globalPos() - self._scroll_drag_start_pos
        if self._dir == ZDirection.Vertical:
            y = max(0, min(new_pos.y(), panel.height() - panel._handle_h.height() - self.height()))
            percentage = y / (panel.height() - panel._handle_h.height() - self.height())
            max_scroll = panel._content.height() - panel.height()
            scroll_pos = int(percentage * max_scroll)
            panel.scrollTo(y=scroll_pos)
        else:
            x = max(0, min(new_pos.x(), panel.width() - panel._handle_v.width() - self.width()))
            percentage = x / (panel.width() - panel._handle_v.width() - self.width())
            max_scroll = panel._content.width() - panel.width()
            scroll_pos = int(percentage * max_scroll)
            panel.scrollTo(x=scroll_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_scroll_dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

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

class ZScrollPanelColorData(ZColorData):
    Body: QColor
    Border: QColor
    Handle: QColor
    HandleBorder: QColor

colordata = {
    'Light':  {
        ZColorDataKey.Body: lambda: ZPalette.PanelBody,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Handle: lambda: ZPalette.ScrollHandle,
        ZColorDataKey.HandleBorder: lambda: ZPalette.ScrollHandle
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.PanelBody,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Handle: lambda: ZPalette.ScrollHandle,
        ZColorDataKey.HandleBorder: lambda: ZPalette.ScrollHandle
    }
}

# region ZScrollPanel
@colordata_provider(datamap=colordata, classtype=ZScrollPanelColorData)
class ZScrollPanel(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZScrollPanelColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZScrollPanel'},
        'radiusCtrl': {'value': 5.0},
    }

    def __init__(self,
                 parent: ZWidget | None = None,
                 objectName: str | None = None,
                 ):
        super().__init__(parent,
                         objectName=objectName)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._content = ZContentWidget(self)
        self._last_v_handle_pos: float = 0.0
        self._last_v_handle_len: float = 0.0
        self._last_h_handle_pos: float = 0.0
        self._last_h_handle_len: float = 0.0
        self._handle_v = ScrollHandle(self,ZDirection.Vertical)
        self._handle_h = ScrollHandle(self,ZDirection.Horizontal)
        self._content.resized.connect(self._update_handles_and_content)
        self._init_color_data_()

    def content(self): return self._content

    # region public
    def scrollTo(self, x: int = None, y: int = None):
        """滚动到指定位置
        Args:
            x(int): 水平滚动位置, None表示不改变
            y(int): 垂直滚动位置, None表示不改变
        """
        current_pos = self._content.pos()
        current_x, current_y = current_pos.x(), current_pos.y()
        if y is not None:
            max_scroll_y = self._content.height() - self.height()
            if max_scroll_y > 0:
                y = max(0, min(y, max_scroll_y))
                current_y = -y
        if x is not None:
            max_scroll_x = self._content.width() - self.width()
            if max_scroll_x > 0:
                x = max(0, min(x, max_scroll_x))
                current_x = -x
        final_x = int(current_x)
        final_y = int(current_y)
        self._content.widgetPositionCtrl.moveTo(final_x, final_y)
        self._sync_scroll_handles(final_x, final_y)


    def layout(self):
        return self._content.layout()

    def setLayout(self, arg__1:QLayout):
        return self._content.setLayout(arg__1)

    # region event
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value
        if self.bodyColorCtrl.color.alpha() > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.bodyColorCtrl.color)
            painter.drawRoundedRect(rect, radius, radius)
        if self.borderColorCtrl.color.alpha() > 0:
            painter.setPen(QPen(self.borderColorCtrl.color, 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5),
                radius, radius
                )
        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = event.size().width(), event.size().height()
        size_hint = self._content.sizeHint()
        content_w = max(size_hint.width(), w)
        content_h = max(size_hint.height(), h)
        # 更新内容区域大小
        self._content.resize(content_w, content_h)
        self._update_handles_and_content()


    def wheelEvent(self, event: QWheelEvent):
        current_x = -self._content.x()
        current_y = -self._content.y()
        ZGlobal.tooltip.windowFadeOut()
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            delta = event.angleDelta().x() if event.angleDelta().x() != 0 else event.angleDelta().y()
            step = delta / 120 * 100
            new_x = current_x - step
            self.scrollTo(x=new_x, y=current_y)
        else:
            delta = event.angleDelta().y()
            step = delta / 120 * 100
            new_y = current_y - step
            self.scrollTo(x=current_x, y=new_y)
        event.accept()

    # region private
    def _init_color_data_(self):
        self._update_handles_and_content()
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border
        self._handle_h.bodyColorCtrl.color = data.Handle
        self._handle_v.bodyColorCtrl.color = data.Handle


    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)
        self._handle_h.bodyColorCtrl.setColorTo(data.Handle)
        self._handle_v.bodyColorCtrl.setColorTo(data.Handle)
        self._handle_h._trans_timer.start(1200)
        self._handle_v._trans_timer.start(1200)

    def _sync_scroll_handles(self, current_x:int, current_y:int):
        """根据内容区位置同步滑块位置"""
        content_height = self._content.height()
        viewport_height = self.height()
        max_scroll_y = content_height - (viewport_height - self._handle_h.height())
        if self._handle_v.isVisible() and max_scroll_y > 0:
            handle_height = self._handle_v.height()
            handle_space = viewport_height - handle_height
            scroll_y = -current_y
            handle_pos = (scroll_y / max_scroll_y) * handle_space
            if (self._last_v_handle_pos != handle_pos):
                self._handle_v.opaque()
            self._last_v_handle_pos = handle_pos
            self._handle_v.widgetPositionCtrl.moveTo(self.width() - self._handle_v.width(),int(handle_pos))
        content_width = self._content.width()
        viewport_width = self.width()
        max_scroll_x = content_width - (viewport_width - self._handle_v.width())
        if self._handle_h.isVisible() and max_scroll_x > 0:
            handle_width = self._handle_h.width()
            handle_space = viewport_width - handle_width
            scroll_x = -current_x
            handle_pos = (scroll_x / max_scroll_x) * handle_space
            if (self._last_h_handle_pos != handle_pos):
                self._handle_h.opaque()
            self._last_h_handle_pos = handle_pos
            self._handle_h.widgetPositionCtrl.moveTo(int(handle_pos),self.height() - self._handle_h.height())


    def _update_handles_and_content(self):
        viewport = self.size()
        content= self._content.size()
        self._update_vertical_handle(content.height(), viewport.height())
        self._update_horizontal_handle(content.width(), viewport.width())


    def _update_vertical_handle(self, ch, vh):
        max_scroll = ch - vh
        if max_scroll <= 0:
            self._handle_v.hide()
            self._content.move(self._content.x(), 0)
            return
        content_visible_ratio = -self._content.y() / ch
        new_scroll_pos = max(0, min(int(content_visible_ratio * ch), max_scroll))
        self._content.widgetPositionCtrl.moveTo(self._content.x(), -new_scroll_pos)
        handle_h= max(30, vh * min(1.0, vh / ch))
        handle_space = vh - handle_h
        handle_pos = (new_scroll_pos / max_scroll) * handle_space
        self._handle_v.show()
        if (self._last_v_handle_pos != handle_pos or
            self._last_v_handle_len != handle_h):
            self._handle_v.opaque()
        self._last_v_handle_pos = handle_pos
        self._last_v_handle_len = handle_h
        self._handle_v.setHandleLengthTo(handle_h)
        self._handle_v.move(self.width() - self._handle_v.width(), self._handle_v.y())
        self._handle_v.widgetPositionCtrl.moveTo(self.width() - self._handle_v.width(),int(handle_pos))


    def _update_horizontal_handle(self, cw, vw):
        max_scroll = cw - vw
        if max_scroll <= 0:
            self._handle_h.hide()
            self._content.move(0, self._content.y())
            return
        content_visible_ratio = -self._content.x() / cw
        new_scroll_pos = max(0, min(int(content_visible_ratio * cw), max_scroll))
        self._content.widgetPositionCtrl.moveTo(new_scroll_pos, self._content.y())
        handle_w = max(30, vw * min(1.0, vw / cw))
        handle_space = vw - handle_w
        handle_pos: int = (new_scroll_pos / max_scroll) * handle_space
        self._handle_h.show()
        if (self._last_h_handle_pos != handle_pos or
            self._last_h_handle_len != handle_w):
            self._handle_h.opaque()
        self._last_h_handle_pos = handle_pos
        self._last_h_handle_len = handle_w
        self._handle_h.setHandleLengthTo(handle_w)
        self._handle_h.move(self._handle_h.x(), self.height() - self._handle_h.height())
        self._handle_h.widgetPositionCtrl.moveTo(int(handle_pos),self.height() - self._handle_h.height())