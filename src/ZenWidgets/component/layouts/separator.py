from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter,QPen,QColor
from ZenWidgets.component.base import (
    ZAnimatedColor,
    ZColorController,
    ZWidget,
)
from ZenWidgets.core import (
    ZDebug,
    ZOrientation
)
from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)
class ZSeparatorColorData(ZColorData):
    Body: QColor

colordata = {
    'Light': {
        ZColorDataKey.Body: lambda: ZPalette.Border,
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.Border,
    }
}
# region ZSeparator
@colordata_provider(datamap=colordata, classtype=ZSeparatorColorData)
class ZSeparator(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[ZSeparatorColorData]
    __controllers_kwargs__ = {'colorDataCtrl':{'key': 'ZSeparator'}}
    def __init__(self,
                 parent: ZWidget | None = None,
                 orientation: ZOrientation = ZOrientation.Horizontal,
                 size: int = 6,
                 line_style: Qt.PenStyle = Qt.PenStyle.SolidLine
                 ):
        super().__init__(parent)
        self._orientation = orientation
        self._size = size
        self._line_style = line_style
        if self._orientation == ZOrientation.Horizontal:
            self.setFixedHeight(self._size)
            self.setMinimumWidth(16)
        elif self._orientation == ZOrientation.Vertical:
            self.setFixedWidth(self._size)
            self.setMinimumHeight(16)
        self._init_color_data_()

    def _init_color_data_(self):
        self.bodyColorCtrl.color = self.colorDataCtrl.data.Body

    def _color_data_change_handler_(self):
        self.bodyColorCtrl.setColorTo(self.colorDataCtrl.data.Body)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(self.bodyColorCtrl.color, 1, self._line_style)
        painter.setPen(pen)
        if self._orientation == ZOrientation.Horizontal:
            y = self.height() // 2
            painter.drawLine(0, y, self.width(), y)
        elif self._orientation == ZOrientation.Vertical:
            x = self.width() // 2
            painter.drawLine(x, 0, x, self.height())
        if ZDebug.draw_rect:
            ZDebug.drawRect(painter, self.rect())
        event.accept()


class ZHSeparator(ZSeparator):
    def __init__(self, parent: ZWidget | None = None, size: int = 6, line_style: Qt.PenStyle = Qt.PenStyle.SolidLine):
        super().__init__(parent=parent, orientation=ZOrientation.Horizontal, size=size, line_style=line_style)


class ZVSeparator(ZSeparator):
    def __init__(self, parent: ZWidget | None = None, size: int = 6, line_style: Qt.PenStyle = Qt.PenStyle.SolidLine):
        super().__init__(parent=parent, orientation=ZOrientation.Vertical, size=size, line_style=line_style)