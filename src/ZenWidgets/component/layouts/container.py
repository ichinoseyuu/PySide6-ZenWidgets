from PySide6.QtGui import QPainter
from PySide6.QtCore import QSize, Qt, QEvent
from PySide6.QtWidgets import QWidget, QSizePolicy
from ZenWidgets.component.base import ZWidget
from ZenWidgets.core.dataclass import ZMargin
from ZenWidgets.core.debug import ZDebug

__all__ = [
    'ZHContainer',
    'ZVContainer'
]
# region - ZHContainer
class ZHContainer(QWidget):
    """水平方向对齐的容器控件，支持不同间距设置和子控件同高功能"""
    def __init__(self,
                 parent: ZWidget | None = None,
                 margin: ZMargin = ZMargin(0, 0, 0, 0),
                 spacing: int = 10,
                 objectName: str | None = None,
                 ):
        super().__init__(parent,
                         objectName=objectName,
                         sizePolicy=QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                         )
        self._alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        self._margin = margin
        self._spacing = spacing
        self._height_expand = False
        self._uniform_height = False
        self._shrinking = False
        self._widgets: list[ZWidget] = []
        self._spacings: list[int] = []

    def widgets(self):
        return self._widgets.copy()

    def margin(self):
        return self._margin

    def setMargin(self, margin: ZMargin):
        if self._margin != margin:
            self._margin = margin
            self.arrangeWidgets()

    def alignment(self):
        return self._alignment

    def setAlignment(self, align: Qt.AlignmentFlag):
        valid_alignments = (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignRight |
                            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignJustify |
                            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignBottom |
                            Qt.AlignmentFlag.AlignVCenter)
        self._alignment = align & valid_alignments
        self.arrangeWidgets()

    def defaultSpacing(self):
        return self._spacing

    def setDefaultSpacing(self, spacing: int):
        if spacing >= 0:
            self._spacing = spacing
            self.arrangeWidgets()

    def isHeightExpand(self):
        return self._height_expand

    def setHeightExpand(self, value: bool):
        if self._height_expand != value:
            self._height_expand = value
            self.arrangeWidgets()

    def isUniformHeight(self):
        return self._uniform_height

    def setUniformHeight(self, value: bool):
        if self._uniform_height != value:
            self._uniform_height = value
            self.arrangeWidgets()

    def addWidget(self, widget: ZWidget, index: int = -1, spacing: int = None):
        """
        添加控件到容器
        index 为插入位置（-1 表示末尾）
        spacing 为插入后与下一个控件之间的间距（用于插入位置右侧）
        """
        if widget in self._widgets:
            return

        if index == -1:
            w_index = len(self._widgets)
        else:
            w_index = max(0, min(index, len(self._widgets)))

        widget.setParent(self)
        # Insert widget into list
        self._widgets.insert(w_index, widget)
        # install event filter so child resize/show/hide triggers rearrange
        widget.installEventFilter(self)

        # manage spacings list: there are always n-1 spacings for n widgets
        if len(self._widgets) > 1:
            new_spacing = spacing if spacing is not None else self._spacing
            # spacing sits between widget[w_index-1] and widget[w_index]; insert at w_index-1
            if w_index == 0:
                # inserted at head -> insert spacing after the new head (between new and old head)
                self._spacings.insert(0, new_spacing)
            else:
                self._spacings.insert(w_index - 1, new_spacing)

        # ensure layout updated
        self.arrangeWidgets()

    def removeWidget(self, widget: ZWidget):
        """从容器移除控件"""
        if widget in self._widgets:
            index = self._widgets.index(widget)
            # remove event filter
            try:
                widget.removeEventFilter(self)
            except Exception:
                pass
            self._widgets.pop(index)
            # remove corresponding spacing
            if self._spacings:
                if index > 0:
                    # remove spacing to the left of removed widget
                    if 0 <= index - 1 < len(self._spacings):
                        self._spacings.pop(index - 1)
                else:
                    # removed first widget -> remove spacing at 0 if exists
                    if 0 < len(self._spacings):
                        self._spacings.pop(0)
            self.arrangeWidgets()
            return
        raise ValueError(f"Widget provided ({widget}) is not in this container.")

    def setSpacing(self, index: int, spacing: int):
        if 0 <= index < len(self._spacings) and spacing >= 0:
            self._spacings[index] = spacing
            self.arrangeWidgets()

    def getSpacing(self, index: int) -> int:
        if 0 <= index < len(self._spacings):
            return self._spacings[index]
        return 0

    def adjustSize(self):
        size = self.sizeHint()
        preferred_w, preferred_h = size.width(), size.height()
        if not self._shrinking:
            preferred_w = max(preferred_w, self.width())
            preferred_h = max(preferred_h, self.height())
        self.resize(preferred_w, preferred_h)

    def sizeHint(self):
        width_used = self._margin.horizontal()
        heights = []
        for obj in self._widgets:
            hint = obj.sizeHint()
            if hint == QSize(-1, -1):
                width_used += obj.width()
                heights.append(obj.height())
            else:
                width_used += hint.width()
                heights.append(hint.height())
        width_used += sum(self._spacings)
        max_height = max(heights) if heights else 0
        max_height += self._margin.vertical()
        return QSize(width_used, max_height)

    def getUsedSpace(self):
        width_used = self._margin.horizontal()
        for obj in self._widgets:
            width_used += obj.width()
        width_used += sum(self._spacings)
        return width_used

    def getSpareSpace(self):
        total_available = self.width() - (self._margin.horizontal())
        used = sum(w.width() for w in self._widgets) + sum(self._spacings)
        return max(0, total_available - used)

    def arrangeWidgets(self):
        """根据对齐方式、间距和边距排列控件"""
        widget_count = len(self._widgets)
        if widget_count == 0:
            return

        spare_space = self.getSpareSpace()

        # 计算起始X坐标（根据水平对齐方式）+ 左边距
        if self._alignment & Qt.AlignmentFlag.AlignLeft:
            left_used = self._margin.left
        elif self._alignment & Qt.AlignmentFlag.AlignRight:
            left_used = self._margin.left + spare_space
        elif self._alignment & Qt.AlignmentFlag.AlignHCenter:
            left_used = self._margin.left + (spare_space // 2)
        else:
            left_used = self._margin.left

        # 可用高度 = 容器高度 - 上下边距
        available_height = self.height() - (self._margin.vertical())

        # 计算子控件的最大高度（如果需要基于子控件最大高度统一设置）
        max_child_height = 0
        if self._height_expand and self._uniform_height:
            max_child_height = max([widget.height() for widget in self._widgets], default=0)

        for i, obj in enumerate(self._widgets):
            # 适应最高控件高度（考虑边距后的可用高度）
            if self._height_expand:
                if self._uniform_height:
                    obj.setFixedHeight(max_child_height)
                else:
                    obj.setFixedHeight(available_height)

            # 垂直对齐计算（基于可用高度）
            if self._alignment & Qt.AlignmentFlag.AlignTop:
                y = self._margin.top
            elif self._alignment & Qt.AlignmentFlag.AlignVCenter:
                y = self._margin.top + (available_height - obj.height()) // 2
            elif self._alignment & Qt.AlignmentFlag.AlignBottom:
                y = self.height() - self._margin.bottom - obj.height()
            else:
                y = self._margin.top

            # 设置控件位置
            obj.move(left_used, y)

            # 累加宽度和间距（最后一个控件不需要加间距）
            left_used += obj.width()
            if i < widget_count - 1:
                left_used += self._spacings[i] if i < len(self._spacings) else self._spacing

    def eventFilter(self, watched, event):
        if watched in self._widgets and event.type() in (QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.Hide):
            self.arrangeWidgets()
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.arrangeWidgets()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()

# region - ZVContainer
class ZVContainer(QWidget):
    """垂直方向对齐的容器控件，支持不同间距设置和子控件同宽功能"""
    def __init__(self,
                 parent: ZWidget | None = None,
                 margin: ZMargin = ZMargin(0, 0, 0, 0),
                 spacing: int = 10,
                 objectName: str | None = None
                 ):
        super().__init__(parent,
                         objectName=objectName,
                         sizePolicy=QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
                         )
        self._alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        self._margin = margin
        self._spacing = spacing
        self._width_expand = False
        self._uniform_width = False
        self._shrinking = False
        self._widgets: list[ZWidget] = []
        self._spacings: list[int] = []

    def widgets(self):
        return self._widgets.copy()

    def margin(self):
        return self._margin

    def setMargin(self, margin: ZMargin):
        if self._margin != margin:
            self._margin = margin
            self.arrangeWidgets()

    def alignment(self):
        return self._alignment

    def setAlignment(self, align: Qt.AlignmentFlag):
        valid_alignments = (Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignRight |
                            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignJustify |
                            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignBottom |
                            Qt.AlignmentFlag.AlignVCenter)
        self._alignment = align & valid_alignments
        self.arrangeWidgets()

    def defaultSpacing(self):
        return self._spacing

    def setDefaultSpacing(self, spacing: int):
        if spacing >= 0:
            self._spacing = spacing
            self.arrangeWidgets()

    def isWidthExpand(self):
        return self._width_expand

    def setWidthExpand(self, value: bool):
        if self._width_expand != value:
            self._width_expand = value
            self.arrangeWidgets()

    def isUniformWidth(self):
        return self._uniform_width

    def setUniformWidth(self, value: bool):
        if self._uniform_width != value:
            self._uniform_width = value
            self.arrangeWidgets()

    def addWidget(self, widget: ZWidget, index: int = -1, spacing: int = None):
        if widget in self._widgets:
            return

        if index == -1:
            w_index = len(self._widgets)
        else:
            w_index = max(0, min(index, len(self._widgets)))

        widget.setParent(self)
        self._widgets.insert(w_index, widget)
        widget.installEventFilter(self)

        if len(self._widgets) > 1:
            new_spacing = spacing if spacing is not None else self._spacing
            if w_index == 0:
                self._spacings.insert(0, new_spacing)
            else:
                self._spacings.insert(w_index - 1, new_spacing)

        self.arrangeWidgets()

    def removeWidget(self, widget: ZWidget):
        if widget in self._widgets:
            index = self._widgets.index(widget)
            try:
                widget.removeEventFilter(self)
            except Exception:
                pass
            self._widgets.pop(index)
            if self._spacings:
                if index > 0:
                    if 0 <= index - 1 < len(self._spacings):
                        self._spacings.pop(index - 1)
                else:
                    if 0 < len(self._spacings):
                        self._spacings.pop(0)
            self.arrangeWidgets()
            return
        raise ValueError(f"Widget provided ({widget}) is not in this container.")

    def setSpacing(self, index: int, spacing: int):
        if 0 <= index < len(self._spacings) and spacing >= 0:
            self._spacings[index] = spacing
            self.arrangeWidgets()

    def getSpacing(self, index: int) -> int:
        if 0 <= index < len(self._spacings):
            return self._spacings[index]
        return 0

    def adjustSize(self):
        size = self.sizeHint()
        preferred_w, preferred_h = size.width(), size.height()
        if not self._shrinking:
            preferred_w = max(preferred_w, self.width())
            preferred_h = max(preferred_h, self.height())
        self.resize(preferred_w, preferred_h)

    def sizeHint(self):
        height_used = self._margin.vertical()
        widths = []
        for obj in self._widgets:
            hint = obj.sizeHint()
            if hint == QSize(-1, -1):
                height_used += obj.height()
                widths.append(obj.width())
            else:
                height_used += hint.height()
                widths.append(hint.width())
        height_used += sum(self._spacings)
        max_width = max(widths) if widths else 0
        max_width += self._margin.horizontal()
        return QSize(max_width, height_used)

    def getUsedSpace(self):
        height_used = self._margin.horizontal()
        for obj in self._widgets:
            height_used += obj.height()
        height_used += sum(self._spacings)
        return height_used

    def getSpareSpace(self):
        total_available = self.height() - (self._margin.vertical())
        used = sum(w.height() for w in self._widgets) + sum(self._spacings)
        return max(0, total_available - used)

    def arrangeWidgets(self):
        widget_count = len(self._widgets)
        if widget_count == 0:
            return

        spare_space = self.getSpareSpace()

        if self._alignment & Qt.AlignmentFlag.AlignTop:
            top_used = self._margin.top
        elif self._alignment & Qt.AlignmentFlag.AlignBottom:
            top_used = self._margin.top + spare_space
        elif self._alignment & Qt.AlignmentFlag.AlignVCenter:
            top_used = self._margin.top + (spare_space // 2)
        else:
            top_used = self._margin.top

        available_width = self.width() - (self._margin.horizontal())

        max_child_width = 0
        if self._width_expand and self._uniform_width:
            max_child_width = max([widget.width() for widget in self._widgets], default=0)

        for i, obj in enumerate(self._widgets):
            if self._width_expand:
                if self._uniform_width:
                    obj.resize(max_child_width, obj.height())
                else:
                    obj.resize(available_width, obj.height())

            if self._alignment & Qt.AlignmentFlag.AlignLeft:
                x = self._margin.left
            elif self._alignment & Qt.AlignmentFlag.AlignHCenter:
                x = self._margin.left + (available_width - obj.width()) // 2
            elif self._alignment & Qt.AlignmentFlag.AlignRight:
                x = self.width() - self._margin.right - obj.width()
            else:
                x = self._margin.left

            obj.move(x, top_used)

            top_used += obj.height()
            if i < widget_count - 1:
                top_used += self._spacings[i] if i < len(self._spacings) else self._spacing

    def eventFilter(self, watched, event):
        if watched in self._widgets and event.type() in (QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.Hide):
            self.arrangeWidgets()
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.arrangeWidgets()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()