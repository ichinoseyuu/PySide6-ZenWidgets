from PySide6.QtWidgets import QSpacerItem, QSizePolicy
from PySide6.QtCore import QSize
from typing import overload

class ZSpacerItem(QSpacerItem):
    """通用 ZSpacerItem，继承自 QSpacerItem。

    参数遵循 QSpacerItem(width, height, hPolicy, vPolicy)。
    """
    def __init__(self,
                 width: int = 0,
                 height: int = 0,
                 hPolicy: QSizePolicy.Policy = QSizePolicy.Expanding,
                 vPolicy: QSizePolicy.Policy = QSizePolicy.Expanding
                 ):
        super().__init__(width, height, hPolicy, vPolicy)

    def setFixedSize(self, w: int, h: int):
        """便捷方法：设置固定大小（将策略设为 Fixed）。"""
        self.changeSize(w, h, QSizePolicy.Fixed, QSizePolicy.Fixed)
        return self

    def setExpanding(self, horizontal: bool = True, vertical: bool = True):
        """便捷方法：设置横向/纵向为 Expanding 策略。"""
        h = QSizePolicy.Expanding if horizontal else QSizePolicy.Minimum
        v = QSizePolicy.Expanding if vertical else QSizePolicy.Minimum
        self.changeSize(self.sizeHint().width(), self.sizeHint().height(), h, v)
        return self


class ZHSpacerItem(ZSpacerItem):
    """水平间隔（横向可伸展）。"""
    def __init__(self, width: int = 0):
        # 横向可伸展，纵向保留最小高度
        super().__init__(width, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)


class ZVSpacerItem(ZSpacerItem):
    """垂直间隔（纵向可伸展）。"""
    def __init__(self, height: int = 0):
        # 纵向可伸展，横向保留最小宽度
        super().__init__(0, height, QSizePolicy.Minimum, QSizePolicy.Expanding)
