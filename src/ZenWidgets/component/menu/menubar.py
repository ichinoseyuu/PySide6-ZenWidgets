import logging
from PySide6.QtCore import Qt,Signal,QMargins,QSize,QTimer
from PySide6.QtGui import QFont,QPainter,QPen,QColor
from PySide6.QtWidgets import QSizePolicy
from ZenWidgets.component.layouts import ZHBoxLayout,ZVSeparator
from ZenWidgets.component.base import (
    ZClickWidget,
    ZWidget,
    ZColorController,
    ZAnimatedColor,
    ZAnimatedFloat,
    ZOpacityEffect,
)
from ZenWidgets.component.menu.menu import ZMenu
from ZenWidgets.core import ZPadding,CoordConverter,ZGlobal
from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

class ZMenubarItemColorData(ZColorData):
    Text: QColor

colordata = {
    'Light': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
    },
    'Dark': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
    }
}

@colordata_provider(datamap=colordata, classtype=ZMenubarItemColorData)
class ZMenubarItem(ZClickWidget):
    triggered = Signal()
    textColorCtrl: ZAnimatedColor
    opacityEffectCtrl: ZOpacityEffect
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZMenubarItemColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl': {'key': 'ZMenubarItem'},
        'radiusCtrl': {'value': 4.0},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 text: str = "",
                 font= QFont("Microsoft YaHei", 10)
                 ):
        super().__init__(
            parent=parent,
            font=font,
            sizePolicy=QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed),
            focusPolicy=Qt.FocusPolicy.TabFocus
        )
        self._text = text
        self._padding = ZPadding(8, 4, 8, 4)
        self.setFixedHeight(28)
        self._menu:ZMenu = None
        self._init_color_data_()

    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.setColorTo(data.Text)

    def _mouse_enter_(self): self.opacityEffectCtrl.setAlphaFTo(0.11)
    def _mouse_leave_(self): self.opacityEffectCtrl.toTransparent()
    def _mouse_press_(self): self.opacityEffectCtrl.setAlphaFTo(0.16)
    def _mouse_release_(self): self.opacityEffectCtrl.setAlphaFTo(0.11)

    def setText(self, t: str):
        if self._text == t: return
        self._text = t
        self.update()

    def text(self) -> str:
        return self._text

    def renderText(self) -> str:
        """返回去除&后的显示文本"""
        return self._text.replace("&", "") if self._text else ""

    def mnemonic(self) -> str | None:
        """返回助记符大写字母（如有）"""
        if self._text and '&' in self._text:
            parts = self._text.split('&')
            if len(parts) >= 2 and parts[1]:
                return parts[1][0].upper()
        return None

    def setMenu(self, menu: ZMenu):
        self._menu = menu

    def sizeHint(self):
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text)
        width = text_width + self._padding.left + self._padding.right
        height = fm.height() + self._padding.top + self._padding.bottom
        return QSize(width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing|
            QPainter.RenderHint.TextAntialiasing|
            QPainter.RenderHint.SmoothPixmapTransform
            )
        rect = self.rect()
        radius = self.radiusCtrl.value
        self.opacityEffectCtrl.drawOpacityLayer(painter, rect, radius)
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(rect)
        painter.setPen(QPen(self.textColorCtrl.color))
        painter.setFont(self.font())
        text_rect = rect.adjusted(self._padding.left, self._padding.top, -self._padding.right, -self._padding.bottom)
        painter.drawText(text_rect, Qt.AlignCenter, self.renderText())
        event.accept()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parentWidget()._item_mouse_pressed(self)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.parentWidget()._item_mouse_released(self)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.parentWidget()._item_mouse_enter(self)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._mouse_enter_()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._mouse_leave_()

class ZMenubar(ZWidget):
    menuTriggered = Signal(str, object)
    def __init__(self,
                 parent: ZWidget | None = None,
                 ):
        super().__init__(parent=parent,
                         focusPolicy=Qt.FocusPolicy.StrongFocus)
        self.setLayout(ZHBoxLayout(self, margins=QMargins(6, 2, 6, 2), spacing=6, alignment=Qt.AlignLeft))
        self._items:ZMenubarItem = []
        self._actived_menu: ZMenu | None = None
        self._pressed_item = None
        self._menu_enabled = False  # 控制菜单是否可打开
        self._trigger_flag = False  # 防止重复触发

    def _item_mouse_pressed(self, item: ZMenubarItem):
        if self._pressed_item is None:
            self._pressed_item = item
        elif self._pressed_item is not item:
            return
        if not self._menu_enabled:
            self._menu_enabled = True
            self._trigger_flag = True
            self._open_menu_for_item(item)
        else:
            self._trigger_flag = False

    def _item_mouse_released(self, item: ZMenubarItem):
        if self._pressed_item is item:
            if not self._trigger_flag:
                self._menu_enabled = False
                if self._actived_menu:
                    self._actived_menu._close_menu_chain()
                    self._actived_menu = None
            self._trigger_flag = False
            self._pressed_item = None

    def _item_mouse_enter(self, item: ZMenubarItem):
        if self._menu_enabled:
            if self._actived_menu is not item._menu:
                self._open_menu_for_item(item)

    def _open_menu_for_item(self, item: ZMenubarItem):
        if self._actived_menu and self._actived_menu is not item._menu:
            self._actived_menu._close_menu_chain()
        if item._menu:
            item._menu.showAt(item.mapToGlobal(item.rect().bottomLeft()),CoordConverter.rectToGlobal(item))
            self._actived_menu = item._menu

    def _menu_closed_handler(self):
        self._actived_menu = None
        self._menu_enabled = False
        self._trigger_flag = False

    def addMenu(self, text: str, menu:ZMenu):
        item = ZMenubarItem(self, text)
        self.layout().addWidget(item)
        self._items.append(item)
        if menu:
            item.setMenu(menu)
            menu.itemSelected.connect(self._menu_closed_handler)
            menu.outClicked.connect(self._menu_closed_handler)
            menu.escapePressed.connect(self._menu_closed_handler)

    def addSeparator(self, size=6, line_style=Qt.PenStyle.SolidLine):
        sep = ZVSeparator(self, size=size, line_style=line_style)
        self.layout().addWidget(sep)
        self.resize(self.sizeHint())

    def keyPressEvent(self, event):
        k = event.key()
        text = event.text().upper()
        if text and event.modifiers() == Qt.AltModifier:
            for item in self._items:
                mnemonic = item.mnemonic()
                if mnemonic == text:
                    widget = ZGlobal.getMouseTopWidget()
                    if isinstance(widget, ZMenubarItem):
                        widget.opacityEffectCtrl.toTransparent()
                    if self._actived_menu is not None:
                        self._actived_menu._close_menu_chain()
                    item._menu.showAt(item.mapToGlobal(item.rect().bottomLeft()),CoordConverter.rectToGlobal(item))
                    self._actived_menu = item._menu
                    return
        if k in (Qt.Key_Right, Qt.Key_Left):
            items = self._items
            if not items: return
            focused = self.focusWidget()
            idx = items.index(focused) if isinstance(focused, ZMenubarItem) else -1
            new = (idx + 1) % len(items) if k == Qt.Key_Left else (idx - 1) % len(items) if idx >=0 else len(items)-1
            items[new].setFocus()
            return
        if k in (Qt.Key_Return, Qt.Key_Enter):
            focused = self.focusWidget()
            if isinstance(focused, ZMenubarItem):
                if self._actived_menu is not None:
                    self._actived_menu._close_menu_chain()
                focused._menu.showAt(focused.mapToGlobal(focused.rect().bottomLeft()),CoordConverter.rectToGlobal(focused))
                self._actived_menu = focused._menu
            return
        super().keyPressEvent(event)