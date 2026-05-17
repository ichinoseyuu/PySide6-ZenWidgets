from PySide6.QtGui import QPainter, QResizeEvent
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtWidgets import QWidget
from typing import overload, Optional, Dict, List, Union
from ZenWidgets.component.base import ZWidget
from ZenWidgets.core import ZDebug

__all__ = ['ZStackContainer']

class ZStackContainer(QWidget):
    def __init__(self,
                 parent: Optional[ZWidget] = None,
                 start_point: QPoint = QPoint(0, 40),
                 hide_last_widget: bool = True,
                 objectName: Optional[str] = None,
                 ):
        super().__init__(parent,
                         objectName=objectName
                         )
        self._widgets: Dict[int, ZWidget] = {}
        self._current_index: Optional[int] = None
        self._last_index: Optional[int] = None
        self._start_point: QPoint = start_point
        self._hide_last_widget: bool = hide_last_widget


    # region public
    def currentWidget(self) -> Optional[ZWidget]: return self._widgets.get(self._current_index)

    def currentWidgetIndex(self) -> Optional[int]: return self._current_index

    def lastWidget(self) -> Optional[ZWidget]: return self._widgets.get(self._last_index)

    @overload
    def widget(self, index: int) -> Optional[ZWidget]: ...

    @overload
    def widget(self, name: str) -> Optional[ZWidget]: ...

    def widget(self, arg: Union[int, str]) -> Optional[ZWidget]:
        if isinstance(arg, int):
            return self._widgets.get(arg)
        elif isinstance(arg, str):
            return next((w for w in self._widgets.values() if w.objectName() == arg), None)
        return None

    def widgets(self) -> List[ZWidget]: return [w for _, w in sorted(self._widgets.items(), key=lambda x: x[0])]

    def widgetCount(self) -> int: return len(self._widgets)

    def addWidget(self, widget: ZWidget, cover: bool = False, anim: bool = False) -> None:
        # 计算新索引（确保索引连续递增）
        new_index = max(self._widgets.keys(), default=-1) + 1
        self._widgets[new_index] = widget

        # 绑定父组件 & 初始化尺寸
        widget.setParent(self)
        widget.resize(self.size())

        if cover:
            # 直接设为当前页
            self.setCurrentWidget(widget, anim)
        else:
            # 首次添加页面时自动设为当前页
            if self._current_index is None:
                self._current_index = new_index
                self.currentWidget().show()
            else:
                # 非当前页默认隐藏（按配置）
                if self._hide_last_widget:
                    widget.hide()


    @overload
    def removeWidget(self, index: int) -> None: ...

    @overload
    def removeWidget(self, name: str) -> None: ...

    def removeWidget(self, arg: Union[int, str]) -> None:
        target_index: Optional[int] = None

        if isinstance(arg, int):
            target_index = arg
        elif isinstance(arg, str):
            target_index = next((k for k, v in self._widgets.items() if v.objectName() == arg), None)

        if target_index is None or target_index not in self._widgets: return

        removing_current = (target_index == self._current_index)
        removed_widget = self._widgets.pop(target_index)

        removed_widget.setParent(None)
        removed_widget.hide()

        if removing_current:
            self._current_index = self._last_index or (max(self._widgets.keys(), default=None) if self._widgets else None)
            if self.currentWidget():
                self.currentWidget().show()
                self.currentWidget().resize(self.size())


    @overload
    def setCurrentWidget(self, name: str, anim: bool = True) -> None: ...

    @overload
    def setCurrentWidget(self, index: int, anim: bool = True) -> None: ...

    @overload
    def setCurrentWidget(self, widget: ZWidget, anim: bool = True) -> None: ...

    def setCurrentWidget(self, arg: Union[int, str, ZWidget], anim: bool = True) -> None:
        target_widget: Optional[ZWidget] = None
        target_index: Optional[int] = None

        if isinstance(arg, int):
            target_index = arg
            target_widget = self._widgets.get(target_index)
        elif isinstance(arg, str):
            target_widget = self.widget(arg)
            if target_widget:
                target_index = next(k for k, v in self._widgets.items() if v == target_widget)
        elif isinstance(arg, ZWidget):
            target_widget = arg
            target_index = next((k for k, v in self._widgets.items() if v == target_widget), None)
        else: raise TypeError(f"ZStackContainer: setCurrentWidget 参数类型错误 {arg}")

        if not target_widget or target_index is None: raise ValueError(f"ZStackContainer: setCurrentWidget 目标页面不存在 {arg}")

        if target_index == self._current_index: return

        self._last_index = self._current_index
        self._current_index = target_index

        target_widget.resize(self.size())
        target_widget.show()

        last_widget = self.lastWidget()
        if last_widget and self._hide_last_widget:
            last_widget.hide()

        if anim:
            target_widget.move(self._start_point)
            target_widget.widgetPositionCtrl.moveTo(0, 0)
        else:
            target_widget.move(0, 0)
            target_widget.raise_()

    def sizeHint(self):
        if current := self.currentWidget():
            return current.sizeHint()
        return QSize(400, 300)


    # region event
    def resizeEvent(self, event:QResizeEvent):
        super().resizeEvent(event)
        new_size = event.size()
        for widget in self._widgets.values():
            widget.resize(new_size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()