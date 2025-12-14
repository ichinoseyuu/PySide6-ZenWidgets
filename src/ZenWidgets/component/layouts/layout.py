from PySide6.QtWidgets import QGridLayout,QBoxLayout,QLayoutItem
from PySide6.QtCore import Qt,QMargins,QSize,QPoint
from ZenWidgets.component.base import ZWidget

__all__ = [
    'ZBoxLayout',
    'ZHBoxLayout',
    'ZVBoxLayout',
    'ZGridLayout'
]

# region ZBoxLayout
class ZBoxLayout(QBoxLayout):
    def __init__(self,
                 direction: QBoxLayout.Direction,
                 parent: ZWidget | None = None):
        super().__init__(direction, parent)

    def allWidgets(self) -> list[ZWidget]:
        widgets = []
        for i in range(self.count()):
            item: QLayoutItem = self.itemAt(i)
            if item.widget():
                widgets.append(item.widget())
        return widgets

    def heightHint(self) -> int: return self.sizeHint().height()

    def widthHint(self) -> int: return self.sizeHint().width()

    def horizontalMargin(self) -> int:
        margins = self.contentsMargins()
        return margins.left() + margins.right()

    def verticalMargin(self) -> int:
        margins = self.contentsMargins()
        return margins.top() + margins.bottom()

    def marginTotalSize(self) -> QSize:
        return QSize(self.horizontalMargin(), self.verticalMargin())

    def topLeftMarginSize(self) -> QSize:
        margins = self.contentsMargins()
        return QSize(margins.left(), margins.top())

    def topRightMarginSize(self) -> QSize:
        margins = self.contentsMargins()
        return QSize(margins.right(), margins.top())

    def bottomLeftMarginSize(self) -> QSize:
        margins = self.contentsMargins()
        return QSize(margins.left(), margins.bottom())

    def bottomRightMarginSize(self) -> QSize:
        margins = self.contentsMargins()
        return QSize(margins.right(), margins.bottom())

    def topLeftMarginPoint(self) -> QPoint:
        margins = self.contentsMargins()
        return QPoint(margins.left(), margins.top())

    def topRightMarginPoint(self) -> QPoint:
        margins = self.contentsMargins()
        return QPoint(margins.right(), margins.top())

    def bottomRightMarginPoint(self) -> QPoint:
        margins = self.contentsMargins()
        return QPoint(margins.right(), margins.bottom())

    def bottomLeftMarginPoint(self) -> QPoint:
        margins = self.contentsMargins()
        return QPoint(margins.left(), margins.bottom())

# region ZHBoxLayout
class ZHBoxLayout(ZBoxLayout):
    def __init__(self,
                 parent: ZWidget | None = None,
                 margins: QMargins = QMargins(6, 6, 6, 6),
                 spacing: int = 6,
                 alignment: Qt.AlignmentFlag | None = None
                 ):
        super().__init__(direction=QBoxLayout.Direction.LeftToRight, parent=parent)
        self.setContentsMargins(margins)
        self.setSpacing(spacing)
        if alignment: self.setAlignment(alignment)


# region ZVBoxLayout
class ZVBoxLayout(ZBoxLayout):
    def __init__(self,
                 parent: ZWidget | None = None,
                 margins: QMargins = QMargins(6, 6, 6, 6),
                 spacing: int = 6,
                 alignment: Qt.AlignmentFlag | None = None
                 ):
        super().__init__(direction=QBoxLayout.Direction.TopToBottom, parent=parent)
        self.setContentsMargins(margins)
        self.setSpacing(spacing)
        if alignment: self.setAlignment(alignment)


class ZGridLayout(QGridLayout):
    def __init__(self,
                 parent: ZWidget | None = None,
                 margins: QMargins = QMargins(6, 6, 6, 6),
                 spacing: int = 6,
                 alignment: Qt.AlignmentFlag | None = None
                 ):
        super().__init__(parent)
        self.setContentsMargins(margins)
        self.setSpacing(spacing)
        if alignment: self.setAlignment(alignment)
