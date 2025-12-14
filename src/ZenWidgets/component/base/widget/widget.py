import inspect
from typing import TypeVar,get_origin,overload,override,Any,Union,Dict,List,Tuple,Optional,Generic,TYPE_CHECKING
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt,QEvent,QPoint,QSize,Slot,Signal,QTimer
from PySide6.QtGui import QMouseEvent,QEnterEvent,QResizeEvent,QMoveEvent
from ZenWidgets.component.base.controller import *
from ZenWidgets.core import make_getter,ZState
from ZenWidgets.gui import StyleT
if TYPE_CHECKING:
    from ZenWidgets.component.layouts.layout import ZBoxLayout
    from ZenWidgets.component.base.group import ZExclusiveToggleGroup

__All__ = [
    'ZWidget',
    'ZPlaceHolderWidget',
    'ZContentWidget',
    'ZClickWidget',
    'ZToggleWidget',
    'ZRepeatClickWidget',
    'ZLongPressWidget',
    'ZProgressWidget'
]

ControllerUnion = Union[
    ZAnimatedColor,
    ZAnimatedOpacity,
    ZAnimatedPoint,
    ZAnimatedPointF,
    ZAnimatedSize,
    ZAnimatedRect,
    ZAnimatedFloat,
    ZAnimatedLinearGradient,
    ZColorController,
    ZFlashEffect,
    ZOpacityEffect,
    ZAnimatedInt
    ]

ControllerT = TypeVar('ControllerT', bound=ControllerUnion)

# region ZWidget
class ZWidget(QWidget, Generic[StyleT]):
    '''ZenWidgets 组件的基类'''
    __controllers_cache__: Dict[type, List[Tuple[str, ControllerT, dict]]] = {}
    '''控制器缓存：键为类，值为控制器信息列表 (属性名称, 注解类型, 初始化参数)'''
    __controllers_types__ = (
        ZAnimatedColor,
        ZAnimatedOpacity,
        ZAnimatedPoint,
        ZAnimatedPointF,
        ZAnimatedSize,
        ZAnimatedRect,
        ZAnimatedFloat,
        ZAnimatedLinearGradient,
        ZColorController,
        ZFlashEffect,
        ZOpacityEffect,
        ZAnimatedInt
    )
    '''支持注解的控制器类型'''
    __controllers_kwargs__: dict[str, Any] = {}
    '''传递到支持注解的控制器的参数'''

    dragged = Signal(QPoint) #拖拽信号
    moved = Signal(QPoint)  #移动信号
    resized = Signal(QSize) #大小每次改变信号

    def __init__(self,
                 parent: Optional['ZWidget'] = None,
                 *args,
                 style: Optional[StyleT] = None,
                 dragable: bool = False,
                 move_anchor: QPoint = QPoint(0, 0),
                 height_for_width: bool = False,
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
        self._create_controllers_()
        self._state: ZState = ZState.Idle
        self._style: Optional[StyleT] = style
        self._move_anchor: QPoint = move_anchor
        self._draggable: bool = dragable
        self._drag_pos: QPoint | None = None
        self._height_for_width = height_for_width
        self._windowOpacityCtrl: ZWindowOpacity = ZWindowOpacity(self)
        self._widgetSizeCtrl: ZWidgetSize = ZWidgetSize(self)
        self._widgetPositionCtrl: ZWidgetPosition = ZWidgetPosition(self)
        self._widgetRectCtrl: ZWidgetRect = ZWidgetRect(self)
        self._opacityCtrl: ZAnimatedOpacity = ZAnimatedOpacity(self)

    # region property
    @property
    def windowOpacityCtrl(self) -> ZWindowOpacity: return self._windowOpacityCtrl

    @property
    def widgetSizeCtrl(self) -> ZWidgetSize: return self._widgetSizeCtrl

    @property
    def widgetPositionCtrl(self) -> ZWidgetPosition: return self._widgetPositionCtrl

    @property
    def widgetRectCtrl(self) -> ZWidgetRect: return self._widgetRectCtrl

    @property
    def opacityCtrl(self) -> ZAnimatedOpacity: return self._opacityCtrl

    # region private method
    @classmethod
    def _resolve_controllers_(cls):
        """解析类的控制器信息，子类不可重写"""
        if cls in cls.__controllers_cache__: return cls.__controllers_cache__[cls]

        allowed_types = cls.__controllers_types__
        controllers_kwargs: dict[str, Any] = {}
        annotations: dict[str, Any] = {}

        # 遍历类的继承链，收集注解和控制器参数
        for base_cls in reversed(cls.__mro__):
            if not issubclass(base_cls, ZWidget): continue
            controllers_kwargs.update(getattr(base_cls, '__controllers_kwargs__', {}))
            annotations.update(getattr(base_cls, '__annotations__', {}))

        # 过滤出属于控制器类型的注解
        controllers_info = []
        for name, annotation in annotations.items():
            origin_type = get_origin(annotation) or annotation
            if inspect.isclass(origin_type) and issubclass(origin_type, allowed_types):
                ckwargs = controllers_kwargs.get(name, {})
                controllers_info.append((name, annotation, ckwargs))

        # 缓存解析结果
        cls.__controllers_cache__[cls] = controllers_info
        return controllers_info

    def _create_controllers_(self) -> None:
        '''创建控制器，子类不可重写'''
        controller_info = self.__class__._resolve_controllers_()

        for name, annotation, ckwargs in controller_info:
            controller = annotation(self, **ckwargs)
            setattr(self, f'_{name}', controller)
            if not hasattr(self.__class__, name): setattr(self.__class__, name, property(make_getter(name)))
            if isinstance(controller, ZColorController): controller.styleChanged.connect(self._color_data_change_handler_)

    def _init_color_data_(self) -> None: ...

    def _color_data_change_handler_(self) -> None: ...

    def _show_tooltip_(self) -> None: ...

    def _hide_tooltip_(self) -> None: ...

    def _init_style_(self) -> None: ...

    def _update_style_(self) -> None: ...


    # region public method
    def state(self) -> ZState: return self._state

    @override
    def style(self) -> Optional[StyleT]: return self._style

    def moveAnchor(self): return self._move_anchor

    def isPressed(self) -> bool: return self._state == ZState.Pressed

    def isHover(self) -> bool: return self._state == ZState.Hover

    def isHidden(self) ->bool: return True if self.windowOpacity() == 0 else False

    def isShowing(self) ->bool: return False if self.windowOpacity() == 0 else True

    def isDraggable(self) -> bool: return self._draggable

    def isMoving(self) -> bool: return self.widgetPositionCtrl.animation.isRunning()

    def isResizing(self) -> bool: return self.widgetSizeCtrl.animation.isRunning()

    def isFading(self) -> bool: return self.opacityCtrl.animation.isRunning()

    def isWindowFading(self) -> bool: return self.windowOpacityCtrl.animation.isRunning()

    @override
    def hasHeightForWidth(self): return self._height_for_width

    def setHeightForWidth(self, h: bool) -> None:
        if h != self._height_for_width: self._height_for_width = h

    def heightHint(self) -> int: return self.sizeHint().height()

    def widthHint(self) -> int: return self.sizeHint().width()

    def setDraggable(self, d: bool) -> None:
        if d != self._draggable: self._draggable = d

    @override
    def setStyle(self, style: StyleT) -> None:
        if self._style is None: raise NotImplementedError('this class is not supported style property')
        if self._style != style:
            self._style = style
            self._update_style_()

    @overload
    def setMoveAnchor(self, x: int, y: int) -> None: ...
    @overload
    def setMoveAnchor(self, pos: QPoint) -> None: ...

    def setMoveAnchor(self, *args): self._move_anchor = QPoint(*args)

    @overload
    def moveTo(self, x: int, y: int) -> None: ...
    @overload
    def moveTo(self, pos: QPoint) -> None: ...

    def moveTo(self, *args): self.widgetPositionCtrl.moveTo(*args)

    @overload
    def resizeTo(self, w: int, h: int) -> None: ...
    @overload
    def resizeTo(self, size: QSize) -> None: ...

    def resizeTo(self, *args): self.widgetSizeCtrl.resizeTo(*args)

    @overload
    def move(self, x: int, y: int) -> None: ...
    @overload
    def move(self, pos: QPoint) -> None: ...

    @override
    def move(self, *args): point = QPoint(*args); super().move(point - self._move_anchor)

    def fadeIn(self) -> None: self.opacityCtrl.fadeIn()

    def fadeOut(self) -> None: self.opacityCtrl.fadeOut()

    def windowFadeIn(self) -> None: self.windowOpacityCtrl.fadeIn()

    def windowFadeOut(self) -> None: self.windowOpacityCtrl.fadeOut()

    @override
    def setEnabled(self, e: bool) -> None:
        if e == self.isEnabled(): return
        if e: self.opacityCtrl.fadeTo(1.0)
        else: self.opacityCtrl.fadeTo(0.3)
        super().setEnabled(e)

    @override
    def parentWidget(self) -> Optional['ZWidget']: return super().parentWidget()

    @override
    def layout(self) -> Optional['ZBoxLayout']: return super().layout()

    # region event
    @override
    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ToolTip: return True
        return super().event(event)

    @override
    def moveEvent(self, event: QMoveEvent):
        super().moveEvent(event)
        self.moved.emit(self.pos())

    @override
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.resized.emit(self.size())

    @override
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if self._draggable and event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.pos()

    @override
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        super().mouseMoveEvent(event)
        if self._draggable and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.pos() - self._drag_pos
            if delta.manhattanLength() >= 5:
                self.dragged.emit(delta)


# region ZPlaceHolderWidget
class ZPlaceHolderWidget(ZWidget):
    '''占位组件'''
    pass


# region ZContentWidget
class ZContentWidget(ZWidget):
    '''内容组件'''
    pass


class ZHoverWidget(ZWidget[StyleT]):
    entered = Signal()
    leaved = Signal()
    def __init__(self,
                 parent: Optional[ZWidget] = None,
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

    def _mouse_enter_(self) -> None: ...

    def _mouse_leave_(self) -> None: ...

    @override
    def enterEvent(self, event: QEnterEvent):
        super().enterEvent(event)
        self._state = ZState.Hover
        self._mouse_enter_()
        self.entered.emit()

    @override
    def leaveEvent(self, event: QEvent):
        super().leaveEvent(event)
        self._state = ZState.Idle
        self._mouse_leave_()
        self.leaved.emit()

# region ZClickWidget
class ZClickWidget(ZHoverWidget[StyleT]):
    pressed = Signal()
    released = Signal()
    clicked = Signal()
    def __init__(self,
                 parent: Optional[ZWidget] = None,
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


# region ZToggleWidget
class ZToggleWidget(ZClickWidget[StyleT]):
    toggled = Signal(bool)
    def __init__(self,
                 parent: Optional[ZWidget] = None,
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
        self._group: Optional['ZExclusiveToggleGroup']= None

    # private method
    def _toggle_(self): ...

    # public method
    def isChecked(self) -> bool: return self._checked

    def setChecked(self, c: bool):
        if c == self._checked: return
        self._checked = c
        self._toggle_()
        self.toggled.emit(self._checked)

    def isCheckable(self) -> bool: return self._checkable

    def setCheckable(self, c: bool): self._checkable = c

    def isGroupMember(self) -> bool: return self._is_group_member

    def setGroup(self, group: 'ZExclusiveToggleGroup'):
        self._group = group
        self._is_group_member = True

    def unsetGroup(self):
        self._group = None
        self._is_group_member = False

    # event
    @override
    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and self._checkable:
            if self.rect().contains(event.position().toPoint()):
                self._checked = True if self._is_group_member else not self._checked
                self._toggle_()
                self.toggled.emit(self._checked)

# region ZRepeatClickWidget
class ZRepeatClickWidget(ZClickWidget[StyleT]):
    def __init__(self,
                 parent: Optional[ZWidget] = None,
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

# region ZLongPressWidget
class ZLongPressWidget(ZClickWidget[StyleT]):
    longPressClicked = Signal()
    '''长按信号'''

    progressCtrl: ZAnimatedFloat
    def __init__(self,
                 parent: Optional[ZWidget] = None,
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

# region ZProgressWidget
class ZProgressWidget(ZClickWidget[StyleT]):
    progressChanged = Signal(float)
    '''进度改变信号'''
    progressFinished = Signal()
    '''进度完成信号'''

    progressCtrl: ZAnimatedFloat
    def __init__(self,
                 parent: Optional[ZWidget] = None,
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