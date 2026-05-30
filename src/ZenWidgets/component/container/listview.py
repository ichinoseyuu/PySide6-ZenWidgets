from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets.component.base import (
    ZWidget,
    ZContentWidget
)
from ZenWidgets.component.layouts import ZVBoxLayout, ZHBoxLayout
from ZenWidgets.component.spareparts import ZListViewHandleH, ZListViewHandleV
from ZenWidgets.core import (
    ZGlobal,
    ZDirection,
)

class ZListView(ZWidget):
    """基础列表视图：仅维护一个滑块(handle)，根据方向响应滚轮滚动。
    子类应使用 `ZDirection.Vertical` 或 `ZDirection.Horizontal`。
    """
    def __init__(self,
                 parent: ZWidget | None = None,
                 direction: ZDirection = ZDirection.Vertical,
                 margins: QMargins = QMargins(0, 0, 0, 0),
                 spacing: int = 0,
                 alignment: Qt.AlignmentFlag | None = None,
                 show_handle: bool = True,
                 objectName: str | None = None,
                 ):
        super().__init__(parent, objectName=objectName)
        self._direction = direction
        self._content = ZContentWidget(self)
        if direction == ZDirection.Vertical:
            self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
            self._content.setLayout(ZVBoxLayout(self._content, margins, spacing, alignment))
            self._handle = ZListViewHandleV(self)
        elif direction == ZDirection.Horizontal:
            self._content.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
            self._content.setLayout(ZHBoxLayout(self._content, margins, spacing, alignment))
            self._handle = ZListViewHandleH(self)
        else:
            raise ValueError(f"Invalid direction: {direction}")
        self._handles_visible = bool(show_handle)
        # 初始可见性使用 setVisible，以兼容不同 handle 实现
        self._handle.opacityCtrl.setOpacity(1.0 if show_handle else 0.0)
        self._content.resized.connect(self._update_handle_and_content)

    def content(self): return self._content

    def layout(self):
        return self._content.layout()

    def setLayout(self, arg__1:QLayout):
        return self._content.setLayout(arg__1)

    def _update_handle_and_content(self):
        if self._direction == ZDirection.Vertical:
            ch = self._content.height()
            vh = self.height()
            max_scroll = ch - vh
            if max_scroll <= 0:
                self._handle.hide()
                self._content.move(self._content.x(), 0)
                return
            handle_h = max(30, vh * min(1.0, vh / ch))
            self._handle.show()
            self._handle.opaque()
            self._handle.setHandleLengthTo(handle_h)
            current_y = -self._content.y()
            handle_space = vh - handle_h
            handle_pos = int((current_y / max_scroll) * handle_space)
            self._handle.move(self.width() - self._handle.width(), self._handle.y())
            self._handle.widgetPositionCtrl.moveTo(self.width() - self._handle.width(), handle_pos)
        else:
            cw = self._content.width()
            vw = self.width()
            max_scroll = cw - vw
            if max_scroll <= 0:
                self._handle.hide()
                self._content.move(0, self._content.y())
                return
            handle_w = max(30, vw * min(1.0, vw / cw))
            self._handle.show()
            self._handle.opaque()
            self._handle.setHandleLengthTo(handle_w)
            current_x = -self._content.x()
            handle_space = vw - handle_w
            handle_pos = int((current_x / max_scroll) * handle_space)
            self._handle.move(self._handle.x(), self.height() - self._handle.height())
            self._handle.widgetPositionCtrl.moveTo(handle_pos, self.height() - self._handle.height())

    def scrollTo(self, x: int = None, y: int = None):
        current_pos = self._content.pos()
        current_x, current_y = current_pos.x(), current_pos.y()
        if self._direction == ZDirection.Vertical:
            if y is not None:
                max_scroll_y = max(0, self._content.height() - self.height())
                if max_scroll_y > 0:
                    y = max(0, min(y, max_scroll_y))
                    current_y = -y
        else:
            if x is not None:
                max_scroll_x = max(0, self._content.width() - self.width())
                if max_scroll_x > 0:
                    x = max(0, min(x, max_scroll_x))
                    current_x = -x
        self._content.widgetPositionCtrl.moveTo(int(current_x), int(current_y))
        self._update_handle_and_content()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = event.size().width(), event.size().height()
        size_hint = self._content.sizeHint()
        content_w = max(size_hint.width(), w)
        content_h = max(size_hint.height(), h)
        # 更新内容区域大小
        self._content.resize(content_w, content_h)
        self._update_handle_and_content()

    def setHandlesVisible(self, visible: bool) -> None:
        self._handles_visible = bool(visible)
        self._handle.opacityCtrl.setOpacity(1.0 if self._handles_visible else 0.0)

    def showHandle(self) -> None: self.setHandlesVisible(True)

    def hideHandle(self) -> None: self.setHandlesVisible(False)

    def handleVisible(self) -> bool: return self._handles_visible

    # event
    def resizeEvent(self, event):
        super().resizeEvent(event)
        w, h = event.size().width(), event.size().height()
        size_hint = self._content.sizeHint()
        content_w = max(size_hint.width(), w)
        content_h = max(size_hint.height(), h)
        # 更新内容区域大小
        self._content.resize(content_w, content_h)
        self._update_handle_and_content()

    def wheelEvent(self, event: QWheelEvent):
        current_x = -self._content.x()
        current_y = -self._content.y()
        ZGlobal.tooltip.windowFadeOut()
        delta = event.angleDelta().y()
        step = delta / 120 * 100
        if self._direction == ZDirection.Vertical:
            new_y = current_y - step
            self.scrollTo(y=new_y)
        else:
            new_x = current_x - step
            self.scrollTo(x=new_x)
        event.accept()

class ZVListView(ZListView):
    def __init__(self, parent: ZWidget | None = None, margins: QMargins = QMargins(6, 6, 6, 6), spacing: int = 6, alignment: Qt.AlignmentFlag | None = None, show_handle: bool = True, objectName: str | None = None):
        super().__init__(parent, ZDirection.Vertical, margins, spacing, alignment, show_handle, objectName)


class ZHListView(ZListView):
    def __init__(self, parent: ZWidget | None = None, margins: QMargins = QMargins(6, 6, 6, 6), spacing: int = 6, alignment: Qt.AlignmentFlag | None = None, show_handle: bool = True, objectName: str | None = None):
        super().__init__(parent, ZDirection.Horizontal, margins, spacing, alignment, show_handle, objectName)