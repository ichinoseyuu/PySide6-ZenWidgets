from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt,Signal,Slot,QTimer
from PySide6.QtGui import QMouseEvent
from ZenWidgets.core import ZState
from ZenWidgets.component.base.widget import ZWidget
from ZenWidgets.component.base.controller import ZAnimatedFloat
from ZenWidgets.gui import StyleT
from typing import TYPE_CHECKING,Optional,override
if TYPE_CHECKING:
    from ZenWidgets.component.base.group import ZExclusiveToggleGroup

__All__ = [
    'ClickInteractiveWidget',
    'ToggleInteractiveWidget',
    'RepeatTriggerWidget',
    'LongPressTriggerWidget',
    'ProgressIndicatorWidget'
]

# region ClickInteractiveWidget
class ClickInteractiveWidget(ZWidget[StyleT]):
    pressed = Signal()
    released = Signal()
    clicked = Signal()
    def __init__(self,
                 parent: QWidget | ZWidget | None = None,
                 *args,
                 style: Optional[StyleT] = None,
                 objectName: str | None = None,
                 toolTip: str | None = None,
                 **kwargs
                 ):
        super().__init__(parent,
                         *args,
                         style=style,
                         objectName=objectName,
                         toolTip=toolTip,
                         **kwargs
                         )

    # private method
    def _mouse_click_(self) -> None: ...

    def _mouse_press_(self) -> None: ...

    def _mouse_release_(self) -> None: ...

    # event
    @override
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._state = ZState.Pressed
            self._mouse_press_()
            self.pressed.emit()

    @override
    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        is_inside = self.rect().contains(event.position().toPoint())
        if self._state != ZState.Pressed and is_inside:
            self._state = ZState.Hover
            self._mouse_enter_()
            self.entered.emit()
        elif self._state != ZState.Pressed and not is_inside:
            self._state = ZState.Idle
            self._mouse_leave_()
            self.leaved.emit()
        elif self._state == ZState.Pressed and not is_inside:
            self._state = ZState.Idle
            self._mouse_release_()
            self.released.emit()
            self._mouse_leave_()
            self.leaved.emit()
        else:
            self._state = ZState.Pressed

    @override
    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_release_()
            self.released.emit()
            if self.rect().contains(event.position().toPoint()):
                self._state = ZState.Hover
                self._mouse_click_()
                self.clicked.emit()
            else:
                self._state = ZState.Idle


# region ToggleInteractiveWidget
class ToggleInteractiveWidget(ClickInteractiveWidget[StyleT]):
    toggled = Signal(bool)
    def __init__(self,
                 parent: QWidget | ZWidget | None = None,
                 *args,
                 checked: bool = False,
                 checkable: bool = True,
                 is_group_member: bool = False,
                 style: Optional[StyleT] = None,
                 objectName: str | None = None,
                 toolTip: str | None = None,
                 **kwargs
                 ):
        super().__init__(parent,
                         *args,
                         style=style,
                         objectName=objectName,
                         toolTip=toolTip,
                         **kwargs
                         )
        self._checkable: bool = checkable
        self._checked: bool = checked
        self._is_group_member: bool = is_group_member
        self._button_group: Optional['ZExclusiveToggleGroup']= None

    # private method
    def _button_toggle_(self): ...

    # public method
    def isChecked(self) -> bool: return self._checked

    def setChecked(self, c: bool):
        if c == self._checked: return
        self._checked = c
        self._button_toggle_()
        self.toggled.emit(self._checked)

    def isCheckable(self) -> bool: return self._checkable

    def setCheckable(self, c: bool): self._checkable = c

    def isGroupMember(self) -> bool: return self._is_group_member

    def setButtonGroup(self, group: 'ZExclusiveToggleGroup'):
        self._button_group = group
        self._is_group_member = True

    def unsetButtonGroup(self):
        self._button_group = None
        self._is_group_member = False

    # event
    @override
    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and self._checkable:
            if self.rect().contains(event.position().toPoint()):
                self._checked = True if self._is_group_member else not self._checked
                self._button_toggle_()
                self.toggled.emit(self._checked)

# region RepeatTriggerWidget
class RepeatTriggerWidget(ClickInteractiveWidget[StyleT]):
    def __init__(self,
                 parent: QWidget | ZWidget | None = None,
                 *args,
                 repeatable: bool = True,
                 interval: int = 50,
                 delay: int = 500,
                 style: Optional[StyleT] = None,
                 objectName: str | None = None,
                 toolTip: str | None = None,
                 **kwargs
                 ):
        super().__init__(parent,
                         *args,
                         style=style,
                         objectName=objectName,
                         toolTip=toolTip,
                         **kwargs
                         )
        self._repeatable = repeatable
        self._repeat_count = 0

        self._trigger_interval = QTimer(self) # 触发间隔
        self._trigger_interval.setInterval(interval)
        self._trigger_interval.timeout.connect(self._mouse_repeat_click_handler_)

        self._trigger_delay = QTimer(self) # 触发延迟
        self._trigger_delay.setSingleShot(True)
        self._trigger_delay.setInterval(delay)
        self._trigger_delay.timeout.connect(self._trigger_interval.start)


    # slot
    @Slot()
    def _mouse_repeat_click_handler_(self):
        '''重复点击时的槽函数'''
        self._repeat_count += 1
        self._mouse_click_()
        self.clicked.emit()

    # public method
    def isRepeatable(self) -> bool: return bool(self._repeatable)

    def setRepeatable(self, r: bool): self._repeatable = r

    def repeatCount(self) -> int: return int(self._repeat_count)

    def triggerInterval(self) -> int: return self._trigger_interval.interval()

    def setTriggerInterval(self, t: int): self._trigger_interval.setInterval(t)

    def triggerDelay(self) -> int: return self._trigger_delay.interval()

    def setTriggerDelay(self, d: int): self._trigger_delay.setInterval(d)

    # event
    @override
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and self._repeatable:
            self._trigger_delay.start()

    @override
    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        if not self.rect().contains(event.position().toPoint()) and self._repeatable:
            self._trigger_delay.stop()
            self._trigger_interval.stop()
            self._repeat_count = 0

    @override
    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and self._repeatable:
            self._trigger_delay.stop()
            self._trigger_interval.stop()
            self._repeat_count = 0

# region LongPressTriggerWidget
class LongPressTriggerWidget(ClickInteractiveWidget[StyleT]):
    longPressClicked = Signal()
    '''长按信号'''

    progressCtrl: ZAnimatedFloat
    def __init__(self,
                 parent: QWidget | ZWidget | None = None,
                 *args,
                 style: Optional[StyleT] = None,
                 objectName: str | None = None,
                 toolTip: str | None = None,
                 **kwargs
                 ):
        super().__init__(parent,
                         *args,
                         style=style,
                         objectName=objectName,
                         toolTip=toolTip,
                         **kwargs
                         )
        self._pressed_timer = QTimer(self)
        self._pressed_timer.setInterval(1000 // 60)
        self._pressed_timer.timeout.connect(self._long_press_handler_)

    # private method
    def _mouse_press_(self):
        self._pressed_timer.start()

    def _mouse_release_(self):
        self._reset_progress_()

    def _step_length_(self) -> float:
        '''计算进度条每次增加的步长'''
        remaining = 1.0 - self.progressCtrl.value
        return min(remaining, max(0.01, remaining / 16 + 0.005))

    def _reset_progress_(self):
        '''重置进度条'''
        self._pressed_timer.stop()
        QTimer.singleShot(150, lambda: self.progressCtrl.setValueTo(0.0))

    def _long_press_handler_(self):
        '''鼠标按压时的进度更新逻辑'''
        if not self.isPressed(): return
        progress = self.progressCtrl.value + self._step_length_()
        if progress >= 1.0:
            progress = 1.0
            self.progressCtrl.setValue(progress)
            self._reset_progress_()
            self.longPressClicked.emit()
        else:
            self.progressCtrl.setValue(progress)

# region ProgressIndicatorWidget
class ProgressIndicatorWidget(ClickInteractiveWidget[StyleT]):
    progressChanged = Signal(float)
    '''进度改变信号'''
    progressFinished = Signal()
    '''进度完成信号'''

    progressCtrl: ZAnimatedFloat
    def __init__(self,
                 parent: QWidget | ZWidget | None = None,
                 *args,
                 reset_on_finish: bool = True,
                 objectName: str | None = None,
                 toolTip: str | None = None,
                 **kwargs
                 ):
        super().__init__(parent,
                         *args,
                         objectName=objectName,
                         toolTip=toolTip,
                         **kwargs
                         )
        self._reset_on_finish = reset_on_finish


    # public method
    def isResetOnFinish(self) -> bool: return self._reset_on_finish

    def setResetOnFinish(self, r: bool) -> None: self._reset_on_finish = r

    def setProgress(self, value: float,/, animate: bool = True) -> None:
        value = max(0.0, min(1.0, value))
        if value == 1.0:
            self.progressCtrl.setValueTo(1.0) if animate else self.progressCtrl.setValue(1.0)
            self.progressChanged.emit(1.0)
            self.progressFinished.emit()
            if self._reset_on_finish:
                QTimer.singleShot(150, lambda: self.progressCtrl.setValueTo(.0))
        else:
            self.progressCtrl.setValueTo(value) if animate else self.progressCtrl.setValue(value)
            self.progressChanged.emit(value)