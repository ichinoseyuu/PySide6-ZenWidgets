import random
from PySide6.QtWidgets import QWidget,QSizePolicy
from PySide6.QtCore import QTimer,QPoint,QRectF,QSize
from PySide6.QtGui import QPainter
from ZenWidgets.component.base import ZWidget
from ZenWidgets.core import ZDebug,ZMargins

__all__ = [
    "ABCFlowContainer",
    "ZFlowContainer",
    "ZMasonryContainer"
]

# region ABCFlowContainer
class ABCFlowContainer(QWidget):
    def __init__(self, parent: ZWidget | None = None):
        super().__init__(parent,sizePolicy=QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        self._widgets:list[ZWidget] = []
        self._dragging_widget:ZWidget = None
        self._margin = ZMargins(8, 8, 8, 8)
        self._spacing = [8, 8]

    def setSpacing(self, horizontal=None, vertical=None):
        if horizontal is not None:
            self._spacing[0] = horizontal
        if vertical is not None:
            self._spacing[1] = vertical

    def widgets(self):
        return self._widgets

    def addWidget(self, widget:ZWidget, arrange=True, ani=True):
        """ Add widget to this container """
        widget.setParent(self)
        self._widgets.append(widget)
        if arrange:
            self.arrangeWidgets(ani=ani)

    def removeWidget(self, widget:ZWidget,
                     has_existence_check: bool = True,
                     delete_later: bool = True,
                     fade_out: bool = False,
                     fade_out_delay: int = 0):
        if widget in self._widgets:
            self._widgets.pop(self._widgets.index(widget))

            if fade_out:
                widget.fadeOut()
                if delete_later:
                    delete_timer = QTimer(widget)
                    delete_timer.singleShot(fade_out_delay + 100, widget.deleteLater)
            else:
                if delete_later:
                    widget.deleteLater()

        elif has_existence_check:
            raise ValueError(f"Widget {widget} is not in this container")
        else:
            pass

    def arrangeWidgets(self, ani=True):
        raise NotImplementedError("arrangeWidgets method must be rewrote.")

    def shuffle(self, **kwargs):
        random.shuffle(self._widgets)
        self.arrangeWidgets(**kwargs)

    def swapByIndex(self, from_index, to_index):
        widget_a = self.widgets()[from_index]
        widget_b = self.widgets()[to_index]
        self._widgets[from_index] = widget_b
        self._widgets[to_index] = widget_a
        self.arrangeWidgets()

    def insertToByIndex(self, from_index, to_index, **kwargs):
        widget = self.widgets()[from_index]
        self._widgets[from_index] = None

        if from_index > to_index:
            self._widgets = self._widgets[:to_index] + [widget] + self._widgets[to_index:]
        else:
            self._widgets = self._widgets[:to_index + 1] + [widget] + self._widgets[to_index + 1:]

        self._widgets.pop(self._widgets.index(None))
        self.arrangeWidgets(**kwargs)

    def regDraggableWidget(self, widget: ZWidget):
        def on_dragging(delta: QPoint):
            if self._dragging_widget is None:
                self._dragging_widget = widget
            current_pos = self._dragging_widget.pos()
            new_pos = current_pos + delta
            new_pos.setX(max(self._margin.left, min(new_pos.x(), self.width() - self._margin.right - widget.width())))
            new_pos.setY(max(self._margin.top, min(new_pos.y(), self.height() - self._margin.bottom - widget.height())))
            self._dragging_widget.moveTo(new_pos)
            self._on_widget_dragged(widget)
        widget.setDraggable(True)
        widget.dragged.connect(on_dragging)

    def _on_widget_dragged(self, dragged_widget: ZWidget):
        dragged_widget.raise_()
        center_point = dragged_widget.geometry().center()

        for widget in self.widgets():
            if widget == dragged_widget:
                continue

            if (widget.geometry().contains(center_point) and (not widget.isMoving())):
                self.insertToByIndex(self.widgets().index(dragged_widget),
                                     self.widgets().index(widget),
                                     no_arrange_exceptions=[dragged_widget])
                self._dragging_widget = None
                break


    def mouseReleaseEvent(self, event):
        if self._dragging_widget:
            self._dragging_widget = None
            self.arrangeWidgets()

    def resizeEvent(self, event):
        self.arrangeWidgets()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()

# region ZFlowContainer
class ZFlowContainer(ABCFlowContainer):
    def __init__(self, parent: ZWidget | None = None):
        super().__init__(parent)
        self._line_height = 32
        self._preferred_height = 0

    def adjustSize(self):
        self.resize(self.width(), self._preferred_height)

    def setLineHeight(self, height, rearrange=True):
        self._line_height = height
        if rearrange:
            self.arrangeWidgets(ani=True)

    def arrangeWidgets(self,
                       ani: bool = True,
                       all_fade_in: bool = False,
                       fade_in_delay: int = 200,
                       fade_in_delay_cumulate_rate: int = 10,
                       no_arrange_exceptions: list[ZWidget]|None = None,
                       no_ani_exceptions: list[ZWidget]|None = None):
        used_width = self._margin.left
        used_height = self._margin.top
        delay_counter = 0
        if no_arrange_exceptions is None:
            no_arrange_exceptions = []
        if no_ani_exceptions is None:
            no_ani_exceptions = []

        for widget in self._widgets:
            available_width = self.width() - self._margin.left - self._margin.right
            size = widget.sizeHint()
            if size == QSize(-1, -1): size = widget.size()
            if available_width - (used_width - self._margin.left) - self._spacing[0] < size.width():
                used_height += self._spacing[1] + self._line_height
                used_width = self._margin.left

            if all_fade_in and (widget not in no_ani_exceptions):
                widget.fadeIn()
            delay_counter += fade_in_delay_cumulate_rate

            if (not ani) or (widget in no_ani_exceptions):
                if (widget in no_arrange_exceptions) is False:
                    widget.move(used_width, used_height)
            else:
                if (widget in no_arrange_exceptions) is False:
                    widget.moveTo(used_width, used_height)

            used_width += size.width() + self._spacing[0]

        self._preferred_height = used_height + self._line_height + self._margin.bottom
        self.adjustSize()

    def sizeHint(self):
        return QSize(self.width(), max(self._preferred_height, 0))

# region ZMasonryContainer
class ZMasonryContainer(ABCFlowContainer):
    def __init__(self, parent: ZWidget | None = None):
        super().__init__(parent)
        self._columns = 2
        self._column_width = 160
        self._preferred_height = 0
        self._auto_adjust_column_amount = False

    def setAutoAdjustColumnAmount(self, state: bool):
        self._auto_adjust_column_amount = state

    def setColumns(self, n: int):
        self._columns = max(1, n)

    def setColumnWidth(self, width: int):
        self._column_width = max(1, width)

    def arrangeWidgets(self, ani=True,
                       no_arrange_exceptions: list[ZWidget]|None = None,
                       no_ani_exceptions: list[ZWidget]|None = None,
                       adjust_size: bool = True):
        columns = max(1, int(self._columns))
        used_height = [self._margin.top for _ in range(columns)]
        if no_arrange_exceptions is None:
            no_arrange_exceptions = []
        if no_ani_exceptions is None:
            no_ani_exceptions = []

        for widget in self._widgets:
            column_index = int(min(range(columns), key=lambda i: used_height[i]))

            if widget not in no_arrange_exceptions:
                x = self._margin.left + column_index * (self._column_width + self._spacing[0])
                y = used_height[column_index]
                if ani and (widget not in no_ani_exceptions):
                    widget.moveTo(x, y)
                else:
                    widget.move(x, y)
            size = widget.sizeHint()
            if size == QSize(-1, -1): size = widget.size()
            used_height[column_index] += size.height() + self._spacing[1]

        self._preferred_height = max(max(used_height) - self._spacing[1], 0) + self._margin.bottom
        if adjust_size:
            self.adjustSize()


    def adjustColumnAmount(self, width=None):
        if width is None:
            width = self.width()
        else:
            self.resize(width, self.height())

        available_width = width - self._margin.left - self._margin.right
        self.setColumns(self.calculateColumnAmount(available_width))
        self.arrangeWidgets()

    def calculateColumnAmount(self, width):
        if self._column_width + self._spacing[0] <= 0:
            return 1
        return max(1, (width + self._spacing[0]) // (self._column_width + self._spacing[0]))

    def adjustSize(self):
        self.resize(self.width(), self._preferred_height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._auto_adjust_column_amount:
            self.adjustColumnAmount()