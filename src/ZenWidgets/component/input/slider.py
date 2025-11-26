from typing import overload
from PySide6.QtCore import QPoint,QPointF,QRect,QRectF,QSize,Qt,Signal
from PySide6.QtGui import QPainter,QPen,QLinearGradient,QKeyEvent,QMouseEvent,QWheelEvent
from ZenWidgets.component.base import (
    ZAnimatedColor,
    ZAnimatedLinearGradient,
    ZAnimatedFloat,
    ZColorController,
    ZWidget
)
from ZenWidgets.core import (
    ZGlobal,
    ZDebug,
    ZPosition,
    ZDirection
)
from ZenWidgets.gui import ZSliderColorData,ZSliderStyle
# region SliderFill
class SliderFill(ZWidget):
    bodyColorCtrl: ZAnimatedLinearGradient
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat

    def paintEvent(self, event) -> None:
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value

        x1, y1, x2, y2 = self.bodyColorCtrl.linearPoints
        gradient = QLinearGradient(
            rect.left() + rect.width() * x1,
            rect.top() + rect.height() * y1,
            rect.left() + rect.width() * x2,
            rect.top() + rect.height() * y2
        )
        if not self.bodyColorCtrl.reverse:
            gradient.setColorAt(0.0, self.bodyColorCtrl.start.color)
            gradient.setColorAt(1.0, self.bodyColorCtrl.end.color)
        else:
            gradient.setColorAt(0.0, self.bodyColorCtrl.end.color)
            gradient.setColorAt(1.0, self.bodyColorCtrl.start.color)
        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)
        event.accept()

# region SliderTrack
class SliderTrack(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat

    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value
        painter.setPen(QPen(self.borderColorCtrl.color, 1.0))
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)
        event.accept()

# region SliderHandle
class SliderHandle(ZWidget):
    innerColorCtrl: ZAnimatedColor
    outerColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    innerScaleCtrl: ZAnimatedFloat
    outerScaleCtrl: ZAnimatedFloat

    def __init__(self, parent: ZWidget | None = None, radius: int = 6):
        super().__init__(parent)
        self._radius = radius
        self._scales = {
            'inner': {'normal': 0.4, 'hover': 0.6, 'pressed': 0.5, 'released': 0.6},
            'outer': {'normal': 0.8, 'hover': 1.0, 'pressed': 1.0, 'released': 1.0}
        }
        self.innerScaleCtrl.setValue(self._scales['inner']['normal'])
        self.outerScaleCtrl.setValue(self._scales['outer']['normal'])
        self.setFixedSize(2 * radius, 2 * radius)

    def parent(self) -> 'ZSlider':
        return super().parent()

    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.Antialiasing)
        center = QPointF(self.width() * 0.5, self.height() * 0.5)
        base_radius = min(self.width(), self.height()) * 0.5 - 1.0

        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(self.outerColorCtrl.color)
        outer_radius = base_radius * self.outerScaleCtrl.value
        painter.drawEllipse(center, outer_radius, outer_radius)

        inner_radius = base_radius * self.innerScaleCtrl.value
        painter.setBrush(self.innerColorCtrl.color)
        painter.drawEllipse(center, inner_radius, inner_radius)

        event.accept()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.innerScaleCtrl.setValueTo(self._scales['inner']['pressed'])
        self.outerColorCtrl.setAlphaTo(150)
        self.borderColorCtrl.setAlphaTo(150)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        slider = self.parent()
        global_pos = event.globalPos()
        local_pos = slider.mapFromGlobal(global_pos) - QPoint(self._radius, self._radius)
        if slider.isHorizontal():
            x = int(max(0, min(local_pos.x(), slider._track_length)))
            slider.setValue(x / max(1, slider._track_length) * slider._max_value)
        else:
            y = int(max(0, min(local_pos.y(), slider._track_length)))
            slider.setValue(slider._max_value - y / max(1, slider._track_length) * slider._max_value)
        self.parent()._show_tooltip_()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.innerScaleCtrl.setValueTo(self._scales['inner']['released'])
        self.outerColorCtrl.setAlphaTo(255)
        self.borderColorCtrl.setAlphaTo(255)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.innerScaleCtrl.setValueTo(self._scales['inner']['hover'])
        self.outerScaleCtrl.setValueTo(self._scales['outer']['hover'])
        self.parent()._show_tooltip_()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.innerScaleCtrl.setValueTo(self._scales['inner']['normal'])
        self.outerScaleCtrl.setValueTo(self._scales['outer']['normal'])
        ZGlobal.tooltip.hideTipDelayed(500)
        self.clearFocus()

# region ZSlider
class ZSlider(ZWidget[ZSliderStyle]):
    valueChanged = Signal(object)
    displayValueChanged = Signal(str)
    colorDataCtrl: ZColorController[ZSliderColorData]
    __controllers_kwargs__ = {'colorDataCtrl':{'key': 'ZSlider'}}
    def __init__(self,
                 parent: ZWidget | None = None,
                 direction: ZDirection = ZDirection.Horizontal,
                 style: ZSliderStyle = ZSliderStyle.Default,
                 scope: tuple[int, int] | tuple[float, float] = (0, 100),
                 step: int|float = 1,
                 step_multiplier: int = 1,
                 accuracy: float = 1,
                 value: int|float = 0,
                 auto_strip_zero: bool = False,
                 length: int = 150,
                 objectName: str | None = None,
                 ):
        super().__init__(parent,
                         style=style,
                         objectName=objectName,
                         focusPolicy=Qt.FocusPolicy.WheelFocus,
                         )
        if direction not in (ZDirection.Horizontal, ZDirection.Vertical): raise ValueError('Invalid direction')
        self._dir = direction
        self._scope = scope
        self._min_value, self._max_value = scope
        self._step = max(step, accuracy)
        self._step_multiplier = step_multiplier
        self._accuracy = accuracy
        self._auto_strip_zero = auto_strip_zero

        self._value: int | float = value
        self._percentage: float = 0.0

        self._track_length: int = 0
        self._track_start: int = 0
        self._track_end: int = 0
        self._min_length: int = max(150, length)

        self._track = SliderTrack(self)
        self._fill = SliderFill(self)
        self._handle = SliderHandle(self, self._style.value.HandleRadius)

        self._handle.widgetPositionCtrl.animation.valueChanged.connect(self._update_fill)
        self._init_color_data_()
        self._init_style_()
        self._init_value_()
        self.resize(self.sizeHint())

    # region public
    def percentage(self) -> float: return self._percentage

    def direction(self) -> ZDirection: return self._dir

    def isHorizontal(self) -> bool: return self._dir == ZDirection.Horizontal

    def isVertical(self) -> bool: return self._dir == ZDirection.Vertical

    def autoStripZero(self) -> bool: return self._auto_strip_zero

    def setAutoStripZero(self, v: bool):
        self._auto_strip_zero = v

    def maxValue(self): return self._max_value

    def setMaxValue(self, m: int | float):
        self._max_value = m
        self._scope = (self._min_value, self._max_value)
        self.setValue(self._value)

    def minValue(self): return self._min_value

    def setMinValue(self, m: int | float):
        self._min_value = m
        self._scope = (self._min_value, self._max_value)
        self.setValue(self._value)

    def step(self) -> int | float: return self._step

    def setStep(self, s: int | float):
        self._step = max(s, self._accuracy)

    def stepMultiplier(self) -> int: return self._step_multiplier

    def setStepMultiplier(self, step_multiplier: int):
        self._step_multiplier = step_multiplier

    def accuracy(self) -> float | int: return self._accuracy

    def setAccuracy(self, accuracy: int | float):
        self._accuracy = accuracy
        self._step = max(self._step, accuracy)
        self.setValue(self._value)

    def scope(self): return self._scope

    def setScope(self, s: tuple):
        self._scope = s
        self._max_value = s[1]
        self._min_value = s[0]
        self.setValue(self._value)

    def displayValue(self) -> str:
        if self._accuracy >= 1:
            s = str(int(round(self._value)))
        else:
            decimal_places = max(0, len(str(self._accuracy).split('.')[-1]))
            s = f"{self._value:.{decimal_places}f}"
            if self._auto_strip_zero:
                s = s.rstrip('0').rstrip('.') if '.' in s else s
        return s

    def value(self) -> int | float:
        if self._accuracy >= 1:
            return int(round(self._value))
        decimal_places = max(0, len(str(self._accuracy).split('.')[-1]))
        return round(self._value, decimal_places)

    def setValue(self, value: float):
        clamped = max(self._min_value, min(value, self._max_value))
        self._value = clamped
        self._percentage = (self._value - self._min_value) / (self._max_value - self._min_value)
        self._update_value()
        self.valueChanged.emit(self.value())
        self.displayValueChanged.emit(self.displayValue())

    @overload
    def stepValue(self, step: int, multiplier: int = 1) -> None:
        "根据步长调整值，使用自定义步进倍数"
        ...
    @overload
    def stepValue(self, step: int) -> None:
        "根据步长调整值，使用默认的步进倍数"
        ...

    def stepValue(self, *args) -> None:
        if len(args) == 1:
            new_value = self._value + args[0] * self._step * self._step_multiplier
            self.setValue(new_value)
        elif len(args) == 2:
            new_value = self._value + args[0] * self._step * args[1]
            self.setValue(new_value)

    def adjustSize(self): self.resize(self.sizeHint())

    def sizeHint(self) -> QSize:
        style = self._style.value
        if self.isHorizontal():
            return QSize(self._min_length + style.HandleRadius * 2, style.TrackWidth)
        else:
            return QSize(style.TrackWidth, self._min_length + style.HandleRadius * 2)



    # region private
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self._track.bodyColorCtrl.color = data.Track
        self._track.borderColorCtrl.color = data.TrackBorder
        self._fill.bodyColorCtrl.start.color = data.FillAreaStart
        self._fill.bodyColorCtrl.end.color = data.FillAreaEnd
        self._fill.borderColorCtrl.color = data.FillAreaBorder
        self._handle.innerColorCtrl.color = data.HandleInner
        self._handle.outerColorCtrl.color = data.HandleOuter
        self._handle.borderColorCtrl.color = data.HandleBorder

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self._track.bodyColorCtrl.setColorTo(data.Track)
        self._track.borderColorCtrl.setColorTo(data.TrackBorder)
        self._fill.bodyColorCtrl.start.setColorTo(data.FillAreaStart)
        self._fill.bodyColorCtrl.end.setColorTo(data.FillAreaEnd)
        self._fill.borderColorCtrl.setColorTo(data.FillAreaBorder)
        self._handle.innerColorCtrl.setColorTo(data.HandleInner)
        self._handle.outerColorCtrl.setColorTo(data.HandleOuter)
        self._handle.borderColorCtrl.setColorTo(data.HandleBorder)

    def _init_style_(self):
        style = self._style.value
        if self.isHorizontal():
            self._fill.bodyColorCtrl.direction = 0
            self.setFixedHeight(2 * style.HandleRadius)
            self.setMinimumWidth(self._min_length + style.HandleRadius * 2)
        else:
            self._fill.bodyColorCtrl.reverse = True
            self._fill.bodyColorCtrl.direction = 1
            self.setFixedWidth(2 * style.HandleRadius)
            self.setMinimumHeight(self._min_length + style.HandleRadius * 2)
        self._update_track_radius()

    def _update_style_(self):
        style = self._style.value
        if self.isHorizontal():
            self._fill.bodyColorCtrl.direction = 0
            self.setFixedHeight(2 * style.HandleRadius)
            self.setMinimumWidth(self._min_length + style.HandleRadius * 2)
        else:
            self._fill.bodyColorCtrl.reverse = True
            self._fill.bodyColorCtrl.direction = 1
            self.setFixedWidth(2 * style.HandleRadius)
            self.setMinimumHeight(self._min_length + style.HandleRadius * 2)
        self._update_track_radius()

    def _init_value_(self):
        clamped = max(self._min_value, min(self._value, self._max_value))
        self._value = clamped
        self._percentage = (self._value - self._min_value) / (self._max_value - self._min_value)
        if self.isHorizontal():
            self._handle.widgetPositionCtrl.setPos(QPoint(self._percentage * self._track_length, 0))
        else:
            self._handle.widgetPositionCtrl.setPos(QPoint(0, self._track_length - self._percentage * self._track_length))

    def _calc_track_length(self):
        return max(self._min_length, (self.width() if self.isHorizontal() else self.height()) - self._style.value.HandleRadius * 2)

    def _update_track_radius(self):
        radius = self._style.value.TrackWidth / 2
        self._track.radiusCtrl.value = radius
        self._fill.radiusCtrl.value = radius

    def _update_track(self):
        # 更新轨道,resizeEvent时调用
        style = self._style.value
        length = self._track_length = self._calc_track_length()
        start = self._track_start = style.HandleRadius
        end = self._track_end = start + length
        width = style.TrackWidth
        percentage = self._percentage

        self._update_track_radius()

        if self.isHorizontal():
            y = (self.height() - width) // 2
            geo_track = QRect(start, y, length, width)
            self._track.setGeometry(geo_track)
            geo_fill = QRect(start, y, length * percentage, width)
            self._fill.setGeometry(geo_fill)
            self._handle.move(length * percentage, 0)
        else:
            x = (self.width() - width) // 2
            geo_track = QRect(x, start, width, length)
            self._track.setGeometry(geo_track)
            fill_height = length * percentage
            geo_fill = QRect(x, end - fill_height, width, fill_height)
            self._fill.setGeometry(geo_fill)
            self._handle.move(0, length - length * percentage)

    def _update_value(self):
        # move handle smoothly via position controller
        if self.isHorizontal():
            self._handle.widgetPositionCtrl.moveTo(int(self._percentage * self._track_length), 0)
        else:
            self._handle.widgetPositionCtrl.moveTo(0, int(self._track_length - self._percentage * self._track_length))

    def _update_fill(self):
        # keep fill synchronized with handle
        style = self._style.value
        if self.isHorizontal():
            self._fill.resize(self._handle.x(), style.TrackWidth)
        else:
            self._fill.setGeometry(
                (self.width() - style.TrackWidth)//2,
                self._handle.y() + self._track_start,
                style.TrackWidth,
                self._track_length - self._handle.y()
                )

    def _show_tooltip_(self):
        pos = ZPosition.Top if self.isHorizontal() else ZPosition.Left
        ZGlobal.tooltip.showTip(
            text=self.displayValue(),
            target=self._handle,
            mode=ZGlobal.tooltip.Mode.TrackTarget,
            position=pos
        )

    # region event
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_track()
        self.resize(self.sizeHint())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        if self.isHorizontal() and (event.key() == Qt.Key.Key_Left or event.key() == Qt.Key.Key_Right):
            step = -1 if event.key() == Qt.Key.Key_Left else 1
            self.stepValue(step)
        elif self.isVertical() and (event.key() == Qt.Key.Key_Up or event.key() == Qt.Key.Key_Down):
            step = 1 if event.key() == Qt.Key.Key_Up else -1
            self.stepValue(step)
        self._show_tooltip_()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            start = self._track_start
            end = self._track_end
            length = self._track_length
            if self.isHorizontal():
                x = min(max(event.x(), start), end)
                percent = (x - start) / length
                value = self._min_value + percent * (self._max_value - self._min_value)
            else:
                y = min(max(event.y(), start), end)
                percent = 1 - (y - start) / length
                value = self._min_value + percent * (self._max_value - self._min_value)
            self.setValue(value)
            self._show_tooltip_()

    def wheelEvent(self, event: QWheelEvent):
        super().wheelEvent(event)
        steps = event.angleDelta().y() / 120
        self.stepValue(steps)
        self._show_tooltip_()
        event.accept()

    def enterEvent(self, event):
        super().enterEvent(event)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        ZGlobal.tooltip.hideTipDelayed(500)
        self.clearFocus()