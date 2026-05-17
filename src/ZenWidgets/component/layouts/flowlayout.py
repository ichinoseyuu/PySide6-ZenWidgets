from PySide6.QtWidgets import QLayout, QWidgetItem, QSizePolicy, QWidget
from PySide6.QtCore import QRect, QSize, QPoint, Qt, QPropertyAnimation, QEasingCurve
from typing import Optional

class ZFlowLayout(QLayout):
    def __init__(self, parent: Optional[QWidget]=None, margin=8, h_spacing=8, v_spacing=8, line_height=32, animate=True):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self._h = h_spacing
        self._v = v_spacing
        self._line_height = line_height
        self._animate = animate

    def setAnimate(self, v: bool):
        self._animate = bool(v)
        self.invalidate()

    def addItem(self, item):
        self._items.append(item)

    def addWidget(self, w):
        self.addItem(QWidgetItem(w))

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return False

    def setLineHeight(self, h):
        self._line_height = h
        self.invalidate()

    def _do_layout(self, rect: QRect, apply_positions: bool):
        left, top, right, bottom = self.getContentsMargins()
        x = rect.x() + left
        y = rect.y() + top
        line_height = self._line_height
        max_width = rect.width() - left - right

        cur_x = x
        cur_y = y
        for item in self._items:
            widget = item.widget()
            hint = widget.sizeHint()
            w = hint.width()
            h = hint.height()

            if cur_x + w - x > max_width and cur_x != x:
                # wrap to next line
                cur_x = x
                cur_y += line_height + self._v

            if apply_positions:
                target_pos = QPoint(cur_x, cur_y)

                if self._animate:
                    # 优先使用 ZWidget 的动画接口（moveTo / resizeTo）
                    try:
                        widget.moveTo(target_pos)
                    except Exception:
                        widget.move(target_pos)
                else:
                    # 立即设置几何
                    widget.move(target_pos)

            cur_x += w + self._h

        # total height: last line + bottom margin
        total_height = (cur_y - rect.y()) + line_height + bottom
        return QSize(rect.width(), max(total_height, 0))

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, apply_positions=True)

    def sizeHint(self):
        parent = self.parentWidget()
        width = parent.width() if parent else 0
        rect = QRect(0, 0, width, 0)
        return self._do_layout(rect, apply_positions=False)

    def minimumSize(self):
        return self.sizeHint()