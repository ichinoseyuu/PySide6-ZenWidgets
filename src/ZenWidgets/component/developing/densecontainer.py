from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget
from ZenWidgets.component.base import ZPlaceHolderWidget

__all__ = [
    'ABCDenseContainer',
    'ZHDenseContainer',
    'ZVDenseContainer'
]

# region ABCDenseContainer
class ABCDenseContainer(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.adjust_widgets_size = False  # 子控件适应高度
        self.shrinking = True  # 调整尺寸方法被调用时，允许尺寸变小
        self.use_moveto = False  # 使用 moveto 方法移动控件而非 move
        self.alignment_ = 0

        self.spacing = 16  # 各个控件间的距离

    def setUseMoveTo(self, b: bool):
        self.use_moveto = b

    def setAdjustWidgetsSize(self, b: bool):
        """设置子控件是否在垂直于容器的方向上自动适应"""
        self.adjust_widgets_size = b

    def setShrinking(self, b: bool):
        """设置调整尺寸方法被调用时，是否尺寸变小"""
        self.shrinking = b

    def setAlignCenter(self, b: bool):
        """设置是否将子控件放置在容器中轴线上"""
        print("Warning: method `setAlignCenter` is deprecated, use setAlignment(Qt.AlignCenter) instead.")  # noqa: T201
        if b is True:
            self.setAlignment(self.alignment() | Qt.AlignCenter)

    def setAlignment(self, alignment):
        self.alignment_ = alignment

    def alignment(self):
        return self.alignment_

    def setSpacing(self, spacing: int):
        """设置控件之间的距离"""
        self.spacing = spacing

    def widgets(self):
        raise NotImplementedError()

    @staticmethod
    def get_widget_except_placeholders(widgets):
        no_placeholders = []
        for widget in widgets:
            if isinstance(widget, ZPlaceHolderWidget) is False:
                no_placeholders.append(widget)
        return no_placeholders

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.adjustSize()  # 使用 with 语句时，自动调节大小

# region ZHDenseContainer
class ZHDenseContainer(ABCDenseContainer):
    """一个可以水平方向紧密靠左或靠右堆叠控件的容器"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets_left = []
        self.widgets_right = []
        self.alignment_ = Qt.AlignTop

    def addPlaceholder(self, length, side="left", index=10000):
        """添加占位符"""
        new_label = ZPlaceHolderWidget(self)
        new_label.setVisible(False)
        new_label.resize(length, 0)
        self.addWidget(new_label, side=side, index=index)

    def addWidget(self, widget, side="left", index=10000):
        """添加子控件，这将调整被添加的控件的父对象为该容器"""
        widget.setParent(self)

        if side != "left" and side != "right":
            raise ValueError(f"意外方向参数 {side}")

        if side == "left":
            self.widgets_left = self.widgets_left[:index] + [widget] + self.widgets_left[index:]
        if side == "right":
            self.widgets_right = self.widgets_right[:index] + [widget] + self.widgets_right[index:]

        self.adjustSize()

    def getUsedSpace(self, side):
        if side not in ["left", "right"]:
            raise ValueError(f"Unexpected side: {side}")
        if side == "left":
            return sum([obj.width() + self.spacing for obj in self.widgets_left])
        if side == "right":
            return sum([obj.width() + self.spacing for obj in self.widgets_right])

    def getSpareSpace(self):
        return self.width() - self.getUsedSpace("left") - self.getUsedSpace("right")

    def widgets(self, side=None):
        if side is None:
            widgets = self.widgets_left + self.widgets_right
        elif side == "left":
            widgets = self.widgets_left
        elif side == "right":
            widgets = self.widgets_right
        else:
            raise ValueError(f"Unexpected side: {side}")
        return self.get_widget_except_placeholders(widgets)

    def removeWidget(self, widget):
        """从容器中移除控件"""
        if widget in self.widgets_left:
            index = self.widgets_left.index(widget)
            self.widgets_left.pop(index)
            return

        if widget in self.widgets_right:
            index = self.widgets_left.index(widget)
            self.widgets_left.pop(index)
            return

        raise ValueError(f"Widget provided ({widget}) is not in this container.")

    def sizeHint(self):
        # 创建计数器
        left_used = 0
        right_used = 0

        # 获取各侧宽度
        for obj in self.widgets_left:
            left_used += obj.width() + self.spacing
        for obj in self.widgets_right:
            right_used += obj.width() + self.spacing

        # 计算总共的宽度，并处理
        total_used = left_used + right_used
        total_used -= 0 if self.widgets_left == [] else self.spacing  # 删去多余的 spacing
        total_used -= 0 if self.widgets_right == [] else self.spacing  # 删去多余的 spacing
        total_used += self.spacing if self.widgets_left + self.widgets_right == [] else 0  # 防止极端情况下两侧控件紧贴
        preferred_w = total_used

        return QSize(preferred_w, max([0] + [widget.height() for widget in (self.widgets_left + self.widgets_right)]))

    def arrangeWidget(self):
        """调整子控件的几何信息。这包括排列子控件，置于中轴线上，以及适应容器s"""
        # 初始化已使用空间的计数器
        left_used = 0
        right_used = 0

        # 左侧控件
        for obj in self.widgets_left:
            # 是否适应容器
            if self.adjust_widgets_size is True:
                obj.resize(obj.width(), self.height())

            # 判断并设置对齐方式
            if (self.alignment_ & Qt.AlignTop) == Qt.AlignTop:
                y = 0
            elif (self.alignment_ & Qt.AlignVCenter) == Qt.AlignVCenter:
                y = (self.height() - obj.height()) // 2
            elif (self.alignment_ & Qt.AlignBottom) == Qt.AlignBottom:
                y = self.height() - obj.height()
            else:
                y = 0

            # 设置位置
            if self.use_moveto is True:
                obj.moveTo(left_used, y)
            else:
                obj.move(left_used, y)

            # 计数器添加控件的宽度和间距
            left_used += obj.width() + self.spacing

        # 右侧控件
        for obj in self.widgets_right:
            # 是否适应容器
            if self.adjust_widgets_size is True:
                obj.resize(obj.width(), self.height())

            # 判断并设置对齐方式
            if (self.alignment_ & Qt.AlignTop) == Qt.AlignTop:
                y = 0
            elif (self.alignment_ & Qt.AlignVCenter) == Qt.AlignVCenter:
                y = (self.height() - obj.height()) // 2
            elif (self.alignment_ & Qt.AlignBottom) == Qt.AlignBottom:
                y = self.height() - obj.height()
            else:
                y = 0

            # 设置位置
            if self.use_moveto is True:
                obj.moveTo(self.width() - obj.width() - right_used, y)
            else:
                obj.move(self.width() - obj.width() - right_used, y)

            # 计数器添加控件的宽度和间距
            right_used += obj.width() + self.spacing

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.arrangeWidget()  # 每当自身尺寸改变时，重新设置控件的位置

    def adjustSize(self):
        """根据自身具有的控件调整自身的大小"""
        # 获取最佳尺寸
        size = self.sizeHint()
        preferred_w, preferred_h = size.width(), size.height()

        if self.shrinking is False:
            # 和原本自身的尺寸比价，取最大者
            preferred_w = max(preferred_w, self.width())
            preferred_h = max(preferred_h, self.height())

        self.resize(preferred_w, preferred_h)


# region ZVDenseContainer
class ZVDenseContainer(ABCDenseContainer):
    """一个可以竖直方向紧密靠上或靠下堆叠控件的容器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets_bottom = []
        self.widgets_top = []
        self.alignment_ = Qt.AlignLeft

    def addPlaceholder(self, length, side="top", index=10000):
        """添加占位符"""
        new_label = ZPlaceHolderWidget(self)
        new_label.setVisible(False)
        new_label.resize(0, length)
        self.addWidget(new_label, side=side, index=index)

    def addWidget(self, widget, side="top", index=10000):
        """添加子控件，这将调整被添加的控件的父对象为该容器"""
        widget.setParent(self)

        if side != "top" and side != "bottom":
            raise ValueError(f"意外方向参数 {side}")

        if side == "bottom":
            self.widgets_bottom = self.widgets_bottom[:index] + [widget] + self.widgets_bottom[index:]
        if side == "top":
            self.widgets_top = self.widgets_top[:index] + [widget] + self.widgets_top[index:]

        self.adjustSize()

    def sizeHint(self):
        # 创建计数器
        bottom_used = 0
        top_used = 0

        # 获取各侧高度
        for obj in self.widgets_bottom:
            bottom_used += obj.height() + self.spacing
        for obj in self.widgets_top:
            top_used += obj.height() + self.spacing

        # 计算总共的高度，并处理
        total_used = bottom_used + top_used
        total_used -= 0 if self.widgets_bottom == [] else self.spacing  # 删去多余的 spacing
        total_used -= 0 if self.widgets_top == [] else self.spacing  # 删去多余的 spacing
        total_used += self.spacing if (self.widgets_bottom != [] and self.widgets_top != []) else 0  # 防止两侧控件紧贴
        preferred_h = total_used

        return QSize(max([0] + [widget.width() for widget in (self.widgets_top + self.widgets_bottom)]), preferred_h)

    def getUsedSpace(self, side):
        if side not in ["top", "bottom"]:
            raise ValueError(f"Unexpected side: {side}")
        if side == "top":
            return sum([obj.height() + self.spacing for obj in self.widgets_top])
        if side == "bottom":
            return sum([obj.height() + self.spacing for obj in self.widgets_bottom])

    def getSpareSpace(self):
        return self.height() - self.getUsedSpace("top") - self.getUsedSpace("bottom")

    def widgets(self, side=None):
        if side is None:
            widgets = self.widgets_top + self.widgets_bottom
        elif side == "top":
            widgets = self.widgets_top
        elif side == "bottom":
            widgets = self.widgets_bottom
        else:
            raise ValueError(f"Unexpected side: {side}")
        return self.get_widget_except_placeholders(widgets)

    def removeWidget(self, widget):
        """从容器中移除控件"""
        if widget in self.widgets_top:
            index = self.widgets_top.index(widget)
            self.widgets_top.pop(index)
            return

        if widget in self.widgets_bottom:
            index = self.widgets_bottom.index(widget)
            self.widgets_bottom.pop(index)
            return

        raise ValueError(f"Widget provided ({widget}) is not in this container.")

    def arrangeWidget(self):  # noqa: C901
        """调整子控件的几何信息。这包括排列子控件，置于中轴线上，以及适应容器"""
        # 初始化已使用空间的计数器
        top_used = 0
        bottom_used = 0

        # 下侧控件
        for obj in self.widgets_top:
            # 是否适应容器
            if self.adjust_widgets_size is True:
                obj.resize(self.width(), obj.height())

            # 判断并设置对齐方式
            if (self.alignment_ & Qt.AlignLeft) == Qt.AlignLeft:
                x = 0
            elif (self.alignment_ & Qt.AlignHCenter) == Qt.AlignHCenter:
                x = (self.width() - obj.width()) // 2
            elif (self.alignment_ & Qt.AlignRight) == Qt.AlignRight:
                x = self.width() - obj.width()
            else:
                x = 0

            # 设置位置
            if self.use_moveto is True:
                obj.moveTo(x, top_used)
            else:
                obj.move(x, top_used)

            # 计数器添加控件的宽度和间距
            top_used += obj.height() + self.spacing

        # 上侧控件
        for obj in self.widgets_bottom:
            # 是否适应容器
            if self.adjust_widgets_size is True:
                obj.resize(self.width(), obj.height())

            # 判断并设置对齐方式
            if (self.alignment_ & Qt.AlignLeft) == Qt.AlignLeft:
                x = 0
            elif (self.alignment_ & Qt.AlignHCenter) == Qt.AlignHCenter:
                x = (self.width() - obj.width()) // 2
            elif (self.alignment_ & Qt.AlignRight) == Qt.AlignRight:
                x = self.width() - obj.width()
            else:
                x = 0

            # 设置位置
            if self.use_moveto is True:
                obj.moveTo(x, self.height() - obj.height() - bottom_used)
            else:
                obj.move(x, self.height() - obj.height() - bottom_used)

            # 计数器添加控件的宽度和间距
            bottom_used += obj.height() + self.spacing

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.arrangeWidget()  # 每当自身尺寸改变时，重新设置控件的位置

    def adjustSize(self):
        """根据自身具有的控件调整自身的大小"""
        # 获取最佳尺寸
        size = self.sizeHint()
        preferred_w, preferred_h = size.width(), size.height()

        if self.shrinking is False:
            # 和原本自身的尺寸比价，取最大者
            preferred_w = max(preferred_w, self.width())
            preferred_h = max(preferred_h, self.height())

        self.resize(preferred_w, preferred_h)