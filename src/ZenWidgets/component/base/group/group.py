from PySide6.QtCore import QObject, Signal
from typing import Dict, List, Optional, Any, overload
from functools import partial
from itertools import count
from ZenWidgets.component.base.widget import ZToggleWidget,ZWidget

# region ZExclusiveToggleGroup
class ZExclusiveToggleGroup(QObject):
    """通用互斥切换控件组管理器,用于管理一组只能有一个被选中的切换控件"""
    toggled = Signal()

    def __init__(self,
                 parent: ZWidget | None = None,
                 allow_uncheck: bool = False
                 ):
        super().__init__(parent)
        self._allow_uncheck = allow_uncheck
        self._widgets: Dict[int, ZToggleWidget] = {}
        self._last_checked_key: Optional[int] = None
        self._checked_key: Optional[int] = None
        self._enabled = True
        self._key_counter = count(0)
        self._callbacks: Dict[int, Any] = {}

    # region private
    def _widget_toggle_handler_(self, key: int, checked: bool):
        if not checked: return
        if not self._enabled or key not in self._widgets: return
        if self._checked_key == key:
            self.toggled.emit()
            return
        if self._checked_key is not None and self._checked_key in self._widgets:
            old_button = self._widgets[self._checked_key]
            old_button.setChecked(False)
            old_button._mouse_leave_()
            old_button.leaved.emit()
        self._last_checked_key = self._checked_key
        self._checked_key = key
        self.toggled.emit()

    # region public
    def isEnabled(self) -> bool: return self._enabled

    def setEnabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        for button in self._widgets.values():
            button.setEnabled(self._enabled)

    def widgets(self) -> List[ZToggleWidget]: return list(self._widgets.values())

    def checkedKey(self) -> Optional[int]: return self._checked_key

    def checkedWidget(self) -> Optional[ZToggleWidget]: return self._widgets.get(self._checked_key)

    def lastCheckedKey(self) -> Optional[int]: return self._last_checked_key

    def lastCheckedWidget(self) -> Optional[ZToggleWidget]: return self._widgets.get(self._last_checked_key)

    def count(self) -> int: return len(self._widgets)

    def allowUncheck(self) -> bool: return self._allow_uncheck

    def setAllowUncheck(self, allow: bool) -> None:
        self._allow_uncheck = bool(allow)
        for widget in self._widgets.values():
            widget.setAllowUncheck(self._allow_uncheck)

    def getWidget(self, key: int) -> Optional[ZToggleWidget]: return self._widgets.get(key)

    def addWidget(self,
                  widget: ZToggleWidget,
                  key: Optional[int] = None,
                  is_checked: bool = False,
                  set_first_checked: bool = True) -> int:

        if key is None:
            while True:
                k = next(self._key_counter)
                if k not in self._widgets:
                    used_key = k
                    break
        else:
            if key in self._widgets:
                raise ValueError(f"Button with key '{key}' already exists")
            used_key = key

        self._widgets[used_key] = widget
        widget.setGroup(self)
        widget.setAllowUncheck(self._allow_uncheck)

        # 创建并保存回调以便将来断开
        cb_toggled = partial(self._widget_toggle_handler_, used_key)
        widget.toggled.connect(cb_toggled)
        self._callbacks[used_key] = cb_toggled

        # 根据参数决定是否设置选中状态
        if is_checked or (len(self._widgets) == 1 and set_first_checked):
            self.toggleTo(used_key)

        return used_key

    @overload
    def removeWidget(self, key: int) -> None: ...

    @overload
    def removeWidget(self, widget: ZToggleWidget) -> None: ...

    def removeWidget(self, arg):
        key_to_remove: Optional[int] = None
        if isinstance(arg, int):
            key_to_remove = arg if arg in self._widgets else None
        else:
            for k, v in self._widgets.items():
                if v is arg:
                    key_to_remove = k
                    break
        if key_to_remove is None: return
        # 断开信号连接
        try:
            toggled_cb = self._callbacks.pop(key_to_remove, (None, None))
            btn = self._widgets[key_to_remove]
            if toggled_cb is not None:
                try:
                    btn.toggled.disconnect(toggled_cb)
                except Exception:
                    pass
        except Exception:
            pass
        # 从容器中移除
        del self._widgets[key_to_remove]

        # 如果移除的是当前选中项，清理状态
        if key_to_remove == self._checked_key:
            self._checked_key = None
            self._last_checked_key = None

    def toggleTo(self, key: int):
        if not self._enabled or key not in self._widgets: return
        if self._checked_key == key: return
        # 取消之前选中
        if self._checked_key is not None and self._checked_key in self._widgets:
            old_button = self._widgets[self._checked_key]
            old_button.setChecked(False)
            old_button._mouse_leave_()
            old_button.leaved.emit()
        # 设置新选中
        new_button = self._widgets[key]
        new_button.setChecked(True)
        self._last_checked_key = self._checked_key
        self._checked_key = key
        self.toggled.emit()

    def toggleToNext(self, clicked: bool = True):
        if not self._widgets or self._checked_key is None: return
        keys = list(self._widgets.keys())
        try:
            idx = keys.index(self._checked_key)
        except ValueError:
            return
        next_key = keys[(idx + 1) % len(keys)]
        self.toggleTo(next_key)
        if clicked: self._widgets[next_key].clicked.emit()

    def toggleToLast(self, clicked: bool = True):
        if not self._widgets or self._checked_key is None: return
        keys = list(self._widgets.keys())
        try:
            idx = keys.index(self._checked_key)
        except ValueError:
            return
        prev_key = keys[(idx - 1) % len(keys)]
        self.toggleTo(prev_key)
        if clicked: self._widgets[prev_key].clicked.emit()
