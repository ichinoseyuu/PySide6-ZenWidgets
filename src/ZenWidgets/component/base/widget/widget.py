import inspect
from typing import TypeVar,get_origin,overload,Any,Union,Dict,List,Tuple,Optional,Generic,TYPE_CHECKING
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt,QEvent,QPoint,QSize,Signal
from PySide6.QtGui import QMouseEvent
from ZenWidgets.component.base.controller import *
from ZenWidgets.core import make_getter,ZState
from ZenWidgets.gui import StyleT
if TYPE_CHECKING: from ZenWidgets.component.layouts.layout import ZBoxLayout

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


    dragged = Signal(QPoint)
    '''拖拽信号'''
    moved = Signal(QPoint)
    '''移动信号'''
    resized = Signal(QSize)
    '''调整大小信号'''
    def __init__(self,
                 parent: Optional['ZWidget'] = None,
                 *args,
                 style: Optional[StyleT] = None,
                 dragable: bool = False,
                 move_anchor: QPoint = QPoint(0, 0),
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

    def _init_color_data_(self) -> None:
        '''初始化颜色数据样式,子类选择实现'''
        ...

    def _color_data_change_handler_(self) -> None:
        '''颜色数据变化槽函数,子类选择实现'''
        ...

    def _show_tooltip_(self) -> None:
        '''显示提示框,子类选择实现'''
        ...

    def _hide_tooltip_(self) -> None:
        '''隐藏提示框,子类选择实现'''
        ...

    # region public method
    def state(self) -> ZState: return self._state

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

    def setDraggable(self, d: bool) -> None:
        if d == self._draggable: return
        self._draggable = d

    def setStyle(self, style: StyleT) -> None:
        if self._style is None: raise NotImplementedError('this class is not supported style property')
        if self._style != style:
            self._style = style
            self._update_style_()

    def _init_style_(self) -> None:
        """样式初始化,子类选择实现"""
        ...

    def _update_style_(self) -> None:
        """样式变更,子类选择实现"""
        ...

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

    def move(self, *args): point = QPoint(*args); super().move(point - self._move_anchor)

    def fadeIn(self) -> None: self.opacityCtrl.fadeIn()

    def fadeOut(self) -> None: self.opacityCtrl.fadeOut()

    def windowFadeIn(self) -> None: self.windowOpacityCtrl.fadeIn()

    def windowFadeOut(self) -> None: self.windowOpacityCtrl.fadeOut()

    def setEnabled(self, e: bool) -> None:
        if e == self.isEnabled(): return
        if e: self.opacityCtrl.fadeTo(1.0)
        else: self.opacityCtrl.fadeTo(0.3)
        super().setEnabled(e)

    def parentWidget(self) -> Optional['ZWidget']: return super().parentWidget()

    def layout(self) -> Optional['ZBoxLayout']: return super().layout()

    def heightHint(self) -> int: return self.sizeHint().height()

    def widthHint(self) -> int: return self.sizeHint().width()

    # region event
    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ToolTip: return True
        return super().event(event)

    def moveEvent(self, event):
        super().moveEvent(event)
        self.moved.emit(self.pos())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit(self.size())

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if self._draggable and event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.pos()

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