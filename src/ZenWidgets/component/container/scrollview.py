from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets.component.base import (
    ZWidget,
    ZContentWidget
)
from ZenWidgets.component.spareparts import ZScrollViewHandleH, ZScrollViewHandleV
from ZenWidgets.core import (
    ZGlobal,
)

# region ZScrollView
class ZScrollView(ZWidget):
    def __init__(self,
                 parent: ZWidget | None = None,
                 show_handles: bool = True,
                 objectName: str | None = None,
                 ):
        super().__init__(parent, objectName=objectName)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._content = ZContentWidget(self)
        self._last_v_handle_pos: float = 0.0
        self._last_v_handle_len: float = 0.0
        self._last_h_handle_pos: float = 0.0
        self._last_h_handle_len: float = 0.0
        self._handle_v = ZScrollViewHandleV(self)
        self._handle_h = ZScrollViewHandleH(self)
        # handles 可见性控制
        self._handles_visible = bool(show_handles)
        self._handle_v.opacityCtrl.setOpacity(1.0 if self._handles_visible else 0.0)
        self._handle_h.opacityCtrl.setOpacity(1.0 if self._handles_visible else 0.0)
        self._content.resized.connect(self._update_handles_and_content)

    def content(self): return self._content

    # region private
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

    def setHandlesVisible(self, visible: bool) -> None:
        """设置滑块的可见性（立即生效）。"""
        self._handles_visible = bool(visible)
        self._handle_v.opacityCtrl.setOpacity(1.0 if self._handles_visible else 0.0)
        self._handle_h.opacityCtrl.setOpacity(1.0 if self._handles_visible else 0.0)

    def showHandles(self) -> None:
        self.setHandlesVisible(True)

    def hideHandles(self) -> None:
        self.setHandlesVisible(False)

    def handlesVisible(self) -> bool:
        return self._handles_visible

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