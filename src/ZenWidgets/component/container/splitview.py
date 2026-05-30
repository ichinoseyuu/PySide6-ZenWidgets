from typing import List, Optional
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QCursor
from ZenWidgets.component.base.widget.widget import ZWidget

class ZSplitView(ZWidget):
    """支持任意分区数量的分割视图。"""
    def __init__(self,
                 parent: ZWidget | None = None,
                 orientation: Qt.Orientation = Qt.Orientation.Horizontal,
                 handle_size: int = 6,
                 initial_ratios: Optional[List[float]] = None,
                 min_sizes: Optional[List[int] | int] = None,
                 objectName: str | None = None):
        super().__init__(parent, objectName=objectName)
        self._orientation = orientation
        self._handle_size = max(1, handle_size)

        self._widgets: List[ZWidget] = []
        self._handles: List[ZWidget] = []
        self._ratios: List[float] = []
        self._min_sizes: List[int] = []
        self._initial_ratios = initial_ratios
        self._initial_min_sizes = min_sizes

    def setWidgets(self, *widgets: ZWidget, initial_ratios: Optional[List[float]] = None, min_sizes: Optional[List[int] | int] = None):
        # 移除旧的子控件与句柄
        for h in self._handles:
            try: h.setParent(None)
            except Exception: pass
        self._handles.clear()

        # 清空并设置新子控件
        for w in self._widgets:
            try: w.setParent(None)
            except Exception: pass
        self._widgets = list(widgets)

        n = len(self._widgets)
        if n < 2: return

        # 初始化比例
        ratios = initial_ratios if initial_ratios is not None else self._initial_ratios
        if ratios and len(ratios) == n:
            total = sum(ratios)
            self._ratios = [r / total for r in ratios]
        else:
            self._ratios = [1.0 / n] * n

        # 初始化最小尺寸
        if min_sizes is None:
            min_sizes = self._initial_min_sizes

        if isinstance(min_sizes, int):
            self._min_sizes = [min_sizes] * n
        elif isinstance(min_sizes, list) and len(min_sizes) == n:
            self._min_sizes = list(min_sizes)
        else:
            self._min_sizes = [0] * n

        # 将子控件设置为此父控件的子元素
        for w in self._widgets:
            w.setParent(self)

        # 创建句柄（n-1 个）
        for i in range(n - 1):
            h = ZWidget(self, objectName=f'split_handle_{i}')
            h.setDraggable(True)
            if self._orientation == Qt.Orientation.Horizontal:
                h.setCursor(QCursor(Qt.CursorShape.SplitHCursor))
            else:
                h.setCursor(QCursor(Qt.CursorShape.SplitVCursor))
            # 绑定索引
            h.dragged.connect(lambda d, idx=i: self._on_handle_dragged(idx, d))
            self._handles.append(h)

        self.update_layout()

    def _on_handle_dragged(self, index: int, delta: QPoint):
        n = len(self._widgets)
        if not (0 <= index < n - 1):
            return

        if self._orientation == Qt.Orientation.Horizontal:
            total = max(1, self.width() - self._handle_size * (n - 1))
            if total <= 0:
                return

            sizes = [int(r * total) for r in self._ratios]
            diff = total - sum(sizes)
            for i in range(diff):
                sizes[i % n] += 1

            dx = int(delta.x())
            if dx > 0:
                # 增加左侧组总和，优先从右侧组中收缩（index+1..n-1）
                shrinkable_right = sum(max(0, sizes[k] - self._min_sizes[k]) for k in range(index + 1, n))
                applied = min(dx, shrinkable_right)
                if applied <= 0:
                    return
                remain = applied
                for k in range(index + 1, n):
                    can = max(0, sizes[k] - self._min_sizes[k])
                    delta_k = min(can, remain)
                    sizes[k] -= delta_k
                    remain -= delta_k
                    if remain == 0:
                        break
                sizes[index] += applied
            elif dx < 0:
                # 减少左侧组（含 index），并将空间分配给右侧 index+1
                grow = -dx
                shrinkable_left = sum(max(0, sizes[k] - self._min_sizes[k]) for k in range(0, index + 1))
                applied = min(grow, shrinkable_left)
                if applied <= 0:
                    return
                remain = applied
                for k in range(index, -1, -1):
                    can = max(0, sizes[k] - self._min_sizes[k])
                    delta_k = min(can, remain)
                    sizes[k] -= delta_k
                    remain -= delta_k
                    if remain == 0:
                        break
                sizes[index + 1] += applied

            # 修正总和误差
            cur_sum = sum(sizes)
            if cur_sum != total:
                diff = total - cur_sum
                # 优先分配到可以扩展的区域
                for k in range(n):
                    sizes[k] += diff
                    break

            self._ratios = [s / total for s in sizes]
        else:
            total = max(1, self.height() - self._handle_size * (n - 1))
            if total <= 0:
                return

            sizes = [int(r * total) for r in self._ratios]
            diff = total - sum(sizes)
            for i in range(diff):
                sizes[i % n] += 1

            dy = int(delta.y())
            if dy > 0:
                shrinkable_down = sum(max(0, sizes[k] - self._min_sizes[k]) for k in range(index + 1, n))
                applied = min(dy, shrinkable_down)
                if applied <= 0:
                    return
                remain = applied
                for k in range(index + 1, n):
                    can = max(0, sizes[k] - self._min_sizes[k])
                    delta_k = min(can, remain)
                    sizes[k] -= delta_k
                    remain -= delta_k
                    if remain == 0:
                        break
                sizes[index] += applied
            elif dy < 0:
                grow = -dy
                shrinkable_up = sum(max(0, sizes[k] - self._min_sizes[k]) for k in range(0, index + 1))
                applied = min(grow, shrinkable_up)
                if applied <= 0:
                    return
                remain = applied
                for k in range(index, -1, -1):
                    can = max(0, sizes[k] - self._min_sizes[k])
                    delta_k = min(can, remain)
                    sizes[k] -= delta_k
                    remain -= delta_k
                    if remain == 0:
                        break
                sizes[index + 1] += applied

            cur_sum = sum(sizes)
            if cur_sum != total:
                diff = total - cur_sum
                for k in range(n):
                    sizes[k] += diff
                    break

            self._ratios = [s / total for s in sizes]

        self.update_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_layout()

    def update_layout(self):
        w = self.width()
        h = self.height()
        n = len(self._widgets)
        if n < 2:
            # 仍然放置可能存在的单个句柄
            if self._handles:
                if self._orientation == Qt.Orientation.Horizontal:
                    self._handles[0].setGeometry(0, 0, self._handle_size, h)
                else:
                    self._handles[0].setGeometry(0, 0, w, self._handle_size)
            return

        if self._orientation == Qt.Orientation.Horizontal:
            content_total = max(1, w - self._handle_size * (n - 1))
            # 计算每个面板宽度（最后一个吸收剩余像素以避免溢出）
            widths = [int(r * content_total) for r in self._ratios]
            diff = content_total - sum(widths)
            for i in range(diff):
                widths[i % n] += 1

            x = 0
            for i in range(n):
                # 最后一个分区吸收剩余，防止累积误差或溢出
                if i == n - 1:
                    w_i = max(0, content_total - sum(widths[:n-1]))
                else:
                    w_i = widths[i]

                self._widgets[i].setGeometry(x, 0, w_i, h)
                x += w_i
                if i < n - 1:
                    self._handles[i].setGeometry(x, 0, self._handle_size, h)
                    x += self._handle_size
        else:
            content_total = max(1, h - self._handle_size * (n - 1))
            heights = [int(r * content_total) for r in self._ratios]
            diff = content_total - sum(heights)
            for i in range(diff):
                heights[i % n] += 1

            y = 0
            for i in range(n):
                if i == n - 1:
                    h_i = max(0, content_total - sum(heights[:n-1]))
                else:
                    h_i = heights[i]

                self._widgets[i].setGeometry(0, y, w, h_i)
                y += h_i
                if i < n - 1:
                    self._handles[i].setGeometry(0, y, w, self._handle_size)
                    y += self._handle_size

    def sizeHint(self) -> QSize:
        # 当未指定固定尺寸时，尝试根据子控件自适应
        n = len(self._widgets)
        if n == 0:
            return QSize(100, 100)

        if self._orientation == Qt.Orientation.Horizontal:
            widths = []
            heights = []
            for w in self._widgets:
                hint = w.sizeHint()
                widths.append(hint.width() if hint.width() > 0 else w.width())
                heights.append(hint.height() if hint.height() > 0 else w.height())
            total_w = sum(widths) + self._handle_size * (n - 1)
            max_h = max(heights) if heights else 0
            return QSize(total_w, max_h)
        else:
            widths = []
            heights = []
            for w in self._widgets:
                hint = w.sizeHint()
                widths.append(hint.width() if hint.width() > 0 else w.width())
                heights.append(hint.height() if hint.height() > 0 else w.height())
            total_h = sum(heights) + self._handle_size * (n - 1)
            max_w = max(widths) if widths else 0
            return QSize(max_w, total_h)


class ZHSplitView(ZSplitView):
    def __init__(self, parent: ZWidget | None = None, handle_size: int = 6, initial_ratios: Optional[List[float]] = None, min_sizes: Optional[List[int] | int] = None, objectName: str | None = None):
        super().__init__(parent, Qt.Orientation.Horizontal, handle_size, initial_ratios, min_sizes, objectName)


class ZVSplitView(ZSplitView):
    def __init__(self, parent: ZWidget | None = None, handle_size: int = 6, initial_ratios: Optional[List[float]] = None, min_sizes: Optional[List[int] | int] = None, objectName: str | None = None):
        super().__init__(parent, Qt.Orientation.Vertical, handle_size, initial_ratios, min_sizes, objectName)