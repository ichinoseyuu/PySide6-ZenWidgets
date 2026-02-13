from typing import Any,Dict,Optional,List,Union,cast
from enum import IntEnum
from functools import partial
from PySide6.QtGui import QPainter,QFont,QPen,QIcon,QPixmap,QColor
from PySide6.QtCore import Qt,QSize,QRect,QRectF,QPointF,Signal,Slot,QMargins,QPoint,QEvent,QObject,QTimer
from PySide6.QtWidgets import QApplication,QSizePolicy
from ZenWidgets.component.layouts import ZVBoxLayout
from ZenWidgets.component.base import (
    ZOpacityEffect,
    ZAnimatedColor,
    ZAnimatedOpacity,
    ZAnimatedFloat,
    ZColorController,
    ZClickWidget,
    ZWidget,
    ZContentWidget,
)
from ZenWidgets.core import (
    ZDebug,
    ZGlobal,
    ZMargins,
    ZPadding
)
from ZenWidgets.gui import (
    ZWidgetEffect,
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

class ZAction(QObject):
    """轻量级的菜单项数据结构，包含文本、值、图标、快捷键、子菜单等属性，以及一个 triggered 信号用于触发事件"""
    triggered = Signal()
    def __init__(self,
                 text: str,
                 parent: QObject | None = None,
                 value: Any = None,
                 icon: QIcon | None = None,
                 shortcut: str | None = None,
                 callback = None,
                 submenu: Union[List['ZAction'], 'ZContextMenu'] | None = None):
        super().__init__(parent)
        self._text = text
        self._value = value
        self._shortcut = shortcut
        self._icon = icon
        self._submenu = submenu
        if callback: self.triggered.connect(callback)

    def text(self) -> str: return self._text
    def value(self) -> Any: return self._value
    def shortcut(self) -> str | None: return self._shortcut
    def icon(self) -> QIcon | None: return self._icon
    def submenu(self) -> Union[List['ZAction'], 'ZContextMenu'] | None: return self._submenu

    def setText(self, t: str): self._text = t
    def setValue(self, v: Any): self._value = v
    def setShortcut(self, s: str | None): self._shortcut = s
    def setIcon(self, i: QIcon | None): self._icon = i
    def setSubmenu(self, s: Union[List['ZAction'], 'ZContextMenu'] | None): self._submenu = s

    def trigger(self) -> None: self.triggered.emit()

class ZContextSeparatorColorData(ZColorData):
    Body: QColor

colordata = {
    'Light': {
        ZColorDataKey.Body: lambda: ZPalette.Border,
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.Border,
    }
}

@colordata_provider(datamap=colordata, classtype=ZContextSeparatorColorData)
class ZContextSeparator(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[ZContextSeparatorColorData]
    __controllers_kwargs__ = {'colorDataCtrl':{'key': 'ZContextSeparator'}}
    def __init__(self, parent: ZWidget | None = None, height: int = 8):
        super().__init__(parent)
        self._height = height
        self.setFixedHeight(self._height)
        self._init_color_data_()

    def _init_color_data_(self):
        self.bodyColorCtrl.color = self.colorDataCtrl.data.Body

    def _color_data_change_handler_(self):
        self.bodyColorCtrl.setColorTo(self.colorDataCtrl.data.Body)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(self.bodyColorCtrl.color, 1)
        painter.setPen(pen)
        y = self.height() // 2
        painter.drawLine(0, y, self.width(), y)
        event.accept()

class ZContextItemColorData(ZColorData):
    Text: QColor
    Icon: QColor
    Indicator: QColor

colordata_1 = {
    'Light': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.Icon: lambda: ZPalette.Icon,
        ZColorDataKey.Indicator: lambda: ZPalette.Primary
    },
    'Dark': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.Icon: lambda: ZPalette.Icon,
        ZColorDataKey.Indicator: lambda: ZPalette.Primary
    }
}

# region ZContextItem
@colordata_provider(datamap=colordata_1, classtype=ZContextItemColorData)
class ZContextItem(ZClickWidget):
    opacityEffectCtrl: ZOpacityEffect
    radiusCtrl: ZAnimatedFloat
    textColorCtrl: ZAnimatedColor
    iconColorCtrl: ZAnimatedColor
    shortcutColorCtrl: ZAnimatedColor
    opacityCtrl: ZAnimatedOpacity
    colorDataCtrl: ZColorController[ZContextItemColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZContextItem'},
        'radiusCtrl': {'value': 4.0},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 text: str | None = None,
                 font=QFont("Microsoft YaHei", 9),
                 icon: QIcon | None = None,
                 shortcut: str | None = None,
                 objectName: str | None = None,
                 sizePolicy: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         font=font,
                         sizePolicy=sizePolicy,
                         focusPolicy=Qt.FocusPolicy.TabFocus
                         )
        self._text: str | None = text
        self._icon: QIcon | None = icon
        self._icon_size = QSize(16, 16)
        self._drop_icon: QIcon = ZGlobal.getBuiltinIcon(u':/icons/arrow_right.svg')
        self._drop_icon_size = QSize(12, 12)
        self._padding = ZPadding(4, 4, 16, 4)
        self._spacing = 4
        self._shortcut: str | None = shortcut
        self._has_submenu = False
        self._bound_action: ZAction | None = None
        self._init_color_data_()
        self.resize(self.sizeHint())

    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text
        self.iconColorCtrl.color = data.Icon
        # shortcut uses same base color but a bit faded
        c = QColor(data.Text)
        c.setAlpha(160)
        self.shortcutColorCtrl.color = c

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.setColorTo(data.Text)
        self.iconColorCtrl.setColorTo(data.Icon)
        c = QColor(data.Text)
        c.setAlpha(160)
        self.shortcutColorCtrl.setColorTo(c)

    def _mouse_enter_(self): self.opacityEffectCtrl.setAlphaFTo(0.11)
    def _mouse_leave_(self): self.opacityEffectCtrl.toTransparent()
    def _mouse_press_(self): self.opacityEffectCtrl.setAlphaFTo(0.16)
    def _mouse_release_(self):
        if self._bound_action and self._bound_action.submenu():
            self.opacityEffectCtrl.setAlphaFTo(0.11)
        else:
            self.opacityEffectCtrl.toTransparent()

    # public methods
    def text(self) -> str: return self._text
    def renderText(self) -> str: return self._text.replace("&", "")
    def icon(self) -> QIcon: return QIcon(self._icon)
    def iconSize(self) -> QSize: return QSize(self._icon_size)
    def spacing(self) -> int: return self._spacing
    def padding(self) -> ZPadding: return self._padding
    def shortcut(self) -> str | None: return self._shortcut

    def setText(self, t: str) -> None:
        if self._text == t: return
        self._text = t
        self.update()

    def setIcon(self, i: QIcon) -> None: self._icon = i; self.update()

    def setIconSize(self, s: QSize) -> None:
        if self._icon_size == s: return
        self._icon_size = s
        self.update()

    def setSpacing(self, s: int) -> None:
        if self._spacing == s: return
        self._spacing = s
        self.update()

    def setPadding(self, p: ZPadding) -> None:
        if self._padding == p: return
        self._padding = p
        self.update()

    def setShortcut(self, s: str | None) -> None:
        if self._shortcut == s: return
        self._shortcut = s
        self.update()

    def sizeHint(self):
        content_height = 0
        if self._icon:
            content_height = max(content_height, self._icon_size.height())
        if self._text:
            text_height = self.fontMetrics().height()
            content_height = max(content_height, text_height)
        total_height = content_height + self._padding.top + self._padding.bottom
        min_height = 26
        total_height = max(total_height, min_height)
        return QSize(self.width(), total_height)

    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
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

        p = self._padding
        fm = self.fontMetrics()
        spacing = self._spacing
        content_rect = rect.adjusted(p.left, p.top, -p.right, -p.bottom)

        # always reserve an icon column (prevents misalignment between items with/without icons)
        icon_right = content_rect.left() + self._icon_size.width() + spacing
        if self._icon:
            icon_y = (content_rect.height() - self._icon_size.height()) // 2 + content_rect.top()
            pixmap = self._icon.pixmap(self._icon_size)
            colored_pixmap = QPixmap(pixmap.size())
            colored_pixmap.fill(Qt.transparent)
            with QPainter(colored_pixmap) as p:
                p.drawPixmap(0, 0, pixmap)
                p.setCompositionMode(QPainter.CompositionMode_SourceIn)
                p.fillRect(colored_pixmap.rect(), self.iconColorCtrl.color)
            painter.drawPixmap(content_rect.left(), icon_y, colored_pixmap)

        # reserve right side for shortcut and submenu arrow (arrow drawn last)
        shortcut_w = fm.horizontalAdvance(self._shortcut) if self._shortcut else 0
        arrow_w = self._drop_icon_size.width() if self._has_submenu else 0
        # reserve spacing between text/shortcut and between shortcut/arrow
        right_reserved = (shortcut_w + spacing if shortcut_w else 0) + (arrow_w if arrow_w else 0)
        # text area between icon_right and content_rect.right() - right_reserved
        text_rect = QRect(
            icon_right,
            content_rect.top(),
            max(0, content_rect.width() - (icon_right - content_rect.left()) - right_reserved),
            content_rect.height()
        )
        if self._text:
            painter.setFont(self.font())
            painter.setPen(self.textColorCtrl.color)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.renderText())

        if self._shortcut:
            # place shortcut left of the submenu arrow (if present)
            shortcut_x = content_rect.right() - arrow_w - (spacing if arrow_w else 0) - shortcut_w
            shortcut_rect = QRect(
                shortcut_x,
                content_rect.top(),
                shortcut_w,
                content_rect.height()
            )
            painter.setFont(self.font())
            painter.setPen(self.shortcutColorCtrl.color)
            painter.drawText(shortcut_rect, Qt.AlignRight | Qt.AlignVCenter, self._shortcut)

        # draw submenu arrow last (to the far right)
        if self._has_submenu:
            pixmap = self._drop_icon.pixmap(self._drop_icon_size)
            colored_pixmap = QPixmap(pixmap.size())
            colored_pixmap.setDevicePixelRatio(self.devicePixelRatioF())
            colored_pixmap.fill(Qt.GlobalColor.transparent)
            painter_pix = QPainter(colored_pixmap)
            painter_pix.drawPixmap(0, 0, pixmap)
            painter_pix.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter_pix.fillRect(colored_pixmap.rect(), self.iconColorCtrl.color)
            painter_pix.end()
            pos = QPoint(rect.right() - arrow_w, content_rect.center().y() - self._drop_icon_size.height()/2 + 2)
            painter.drawPixmap(pos, colored_pixmap)

        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._mouse_enter_()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._mouse_leave_()

class ZContextMenuColorData(ZColorData):
    Body: QColor
    Border: QColor

colordata_2 = {
    'Light': {
        ZColorDataKey.Body: lambda: ZPalette.PanelBody,
        ZColorDataKey.Border: lambda: ZPalette.Border
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.PanelBody,
        ZColorDataKey.Border: lambda: ZPalette.Border
    }
}

# region ZContextMenu
@colordata_provider(datamap=colordata_2, classtype=ZContextMenuColorData)
class ZContextMenu(ZWidget):
    itemSelected = Signal(str, object)
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZContextMenuColorData]

    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZContextMenu'},
        'radiusCtrl': {'value': 5.0},
    }
    def __init__(self, parent: ZWidget | None = None, actions: list[ZAction] | None = None):
        super().__init__(parent=parent,f=Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._margin = ZMargins(8, 8, 8, 8)
        self._content = ZContentWidget(self)
        self._content.setLayout(ZVBoxLayout(self, margins=QMargins(4, 4, 4, 4), spacing=2))
        self._content.move(self._margin.left, self._margin.top)
        self._actions: list[ZAction] = []
        self._submenus: dict[str, 'ZContextMenu'] = {}
        self._hover_timer: QTimer = QTimer(self, interval=100)
        self._active_submenu: Optional['ZContextMenu'] = None
        self._parent_menu: Optional['ZContextMenu'] = None
        self._parent_item: Optional['ZContextItem'] = None
        if actions:
            for a in list(actions):
                self.addAction(a)

        self.windowOpacityCtrl.completelyHide.connect(self.close)
        self._init_color_data_()
        self.resize(self.sizeHint())

    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)

    def _action_triggered_handler_(self, action: ZAction):
        # called after action.trigger() -> action.triggered emitted -> we end up here
        self.itemSelected.emit(action.text(), action.value())
        self.windowOpacityCtrl.fadeOut()

    def _get_valid_pos(self, target_pos: QPoint) -> QPoint:
        menu_size = self.sizeHint()
        screen = QApplication.screenAt(target_pos) or QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        x, y = target_pos.x(), target_pos.y()

        if self._parent_item:
            parent_item = self._parent_item
            parent_left = parent_item.mapToGlobal(parent_item.rect().topLeft()).x()
            # 简化x轴修正：移除多余的h计算，仅保留基础左移
            if x + menu_size.width() > screen_geo.right():
                m = self._content.layout().contentsMargins().left() + self._content.layout().contentsMargins().right()
                x = parent_left - menu_size.width() + m - 1
            # 高度修正不变
            if y + menu_size.height() > screen_geo.bottom():
                y = screen_geo.bottom() - menu_size.height()
                y = max(y, screen_geo.top())
        else:
            # 根菜单逻辑不变
            if x + menu_size.width() > screen_geo.right():
                x = screen_geo.right() - menu_size.width()
            x = max(x, screen_geo.left())
            if y + menu_size.height() > screen_geo.bottom():
                y = screen_geo.bottom() - menu_size.height()
            y = max(y, screen_geo.top())

        x = max(min(x, screen_geo.right() - menu_size.width()), screen_geo.left())
        y = max(min(y, screen_geo.bottom() - menu_size.height()), screen_geo.top())
        return QPoint(x, y)

    def _open_submenu_for_item(self, item: ZContextItem, action: ZAction):
        # 打开一个子菜单
        submenu = self._submenus.get(action)
        if not submenu: return
        if self._active_submenu and self._active_submenu is not self._submenus.get(action):
            self._active_submenu.windowOpacityCtrl.fadeOut()
        #origin_pos = item.mapToGlobal(item.rect().topRight()) + QPoint(2, -self._content.layout().contentsMargins().top())
        origin_pos = item.mapToGlobal(item.rect().topRight()) + QPoint(2, 0)
        submenu.showAt(origin_pos)
        submenu._parent_menu = self
        submenu._parent_item = item
        self._active_submenu = submenu
        # when submenu emits optionChanged, bubble and close both menus
        submenu.itemSelected.connect(lambda t, v: (self.itemSelected.emit(t, v), self.windowOpacityCtrl.fadeOut()))

    def _hover_inside_menu_tree(self, menu: 'ZContextMenu', pos: QPoint) -> bool:
        # 递归检查位置是否在菜单范围内（包括活跃子菜单）
        r = QRect(menu.mapToGlobal(menu.rect().topLeft()), menu.mapToGlobal(menu.rect().bottomRight()))
        if r.contains(pos):
            return True
        if menu._active_submenu:
            return self._hover_inside_menu_tree(menu._active_submenu, pos)
        return False

    def _close_menu_and_descendants(self, menu: 'ZContextMenu') -> None:
        if hasattr(menu, '_active_submenu') and menu._active_submenu:
            self._close_menu_and_descendants(menu._active_submenu)
        try: menu.windowOpacityCtrl.fadeOut()
        except: pass

    def _item_entered_handler_(self):
        item: ZContextItem = self.sender()
        self._hover_timer.timeout.connect(
            partial(self._open_submenu_for_item, item, item._bound_action)
        )
        self._hover_timer.start()

    def _item_leaved_handler_(self):
        self._hover_timer.stop()
        self._hover_timer.timeout.disconnect()

    def getActionByText(self, text: str) -> Optional[ZAction]:
        """通过文本获取ZAction实例，核心查询方法，为所有派生查询提供基础"""
        return next((a for a in self._actions if a.text() == text), None)

    def getActionValueByText(self, text: str) -> Any:
        """通过文本获取ZAction绑定的value，替代原_options[text]"""
        action = self.getActionByText(text)
        return action.value() if action else None

    def getActionShortcutByText(self, text: str) -> Optional[str]:
        """通过文本获取ZAction的shortcut，替代原_shortcuts[text]"""
        action = self.getActionByText(text)
        return action.shortcut() if action else None

    def getActionTexts(self) -> List[str]:
        """获取所有Action的文本列表，替代原_items"""
        return [a.text() for a in self._actions]

    def getActionMap(self) -> Dict[str, ZAction]:
        """获取 文本:ZAction 映射字典，按需生成，避免长期维护"""
        return {a.text(): a for a in self._actions}

    def addAction(self, action: ZAction):
        self._actions.append(action)
        item = ZContextItem(self, text=action.text(), icon=action.icon(), shortcut=action.shortcut())
        item._bound_action = action
        self._content.layout().addWidget(item)

        # # submenu handling
        submenu_spec = action.submenu()
        if submenu_spec:
            item._has_submenu = True
            # create submenu instance (if list provided)
            if isinstance(submenu_spec, ZContextMenu):
                submenu = submenu_spec
            else:
                submenu = ZContextMenu(parent=self, actions=submenu_spec)
            submenu._parent_menu = self
            submenu._parent_item = item
            # store mapping
            self._submenus[action] = submenu

            # open submenu on hover or click
            #item.clicked.connect(lambda *_, it=item, a=action: self._open_submenu_for_item(it, a))
            item.entered.connect(self._item_entered_handler_)
            item.leaved.connect(self._item_leaved_handler_)
        # normal action (no submenu)
        else:
            item.clicked.connect(lambda _=None, a=action: a.trigger())

        # action.triggered -> close chain and emit
        action.triggered.connect(lambda _=None, a=action: self._action_triggered_handler_(a))

    def addSeparator(self):
        sep = ZContextSeparator(self)
        self._content.layout().addWidget(sep)
        self.resize(self.sizeHint())

    def addActions(self, actions: list[ZAction]):
        for a in actions: self.addAction(a)

    def removeAction(self, action_or_text):
        text = action_or_text.text() if isinstance(action_or_text, ZAction) else action_or_text
        for child in self._content.findChildren(ZContextItem):
            if child.text() == text:
                try:
                    child.clicked.disconnect()
                except:
                    pass
                child.deleteLater()
                self._content.layout().removeWidget(child)
                break
        target_action = self.getActionByText(text)
        if target_action in self._actions:
            self._actions.remove(target_action)
        self.resize(self.sizeHint())

    def showAt(self, pos: QPoint):
        QApplication.instance().installEventFilter(self)
        super().show()
        self.move(self._get_valid_pos(pos - self._margin.topLeft()))
        #self.move(pos - self._margin.topLeft())
        self.widgetSizeCtrl.resizeFromTo(QSize(self.widthHint(),0),self.sizeHint())
        self.setFocus(Qt.FocusReason.PopupFocusReason)
        self.windowOpacityCtrl.fadeIn()
        self.activateWindow()
        self.raise_()

    def close(self):
        QApplication.instance().removeEventFilter(self)
        super().close()

    def eventFilter(self, obj, event):
        # intercept wheel events while menu is visible to avoid unwanted scrolling
        if self.isVisible() and event.type() == QEvent.Type.Wheel:
            return True

        # auto-hide active submenu when mouse moves outside it (and outside its parent item)
        if self.isVisible() and event.type() == QEvent.Type.MouseMove:
            # get global mouse position (compat for Qt6/Qt5)
            pos = None
            if hasattr(event, 'globalPos'):
                try: pos = event.globalPos()
                except: pos = None
            if pos is None and hasattr(event, 'globalPosition'):
                try: pos = event.globalPosition().toPoint()
                except: pos = None

            if pos is not None and self._active_submenu:
                sub = self._active_submenu
                inside_sub = self._hover_inside_menu_tree(sub, pos)
                inside_parent_item = False
                try:
                    pi = sub._parent_item
                    if pi:
                        pr = QRect(pi.mapToGlobal(pi.rect().topLeft()), pi.mapToGlobal(pi.rect().bottomRight()))
                        inside_parent_item = pr.contains(pos)
                except: pass
                # if mouse is outside the submenu and outside the menu item that opened it -> close submenu only
                if not (inside_sub or inside_parent_item):
                    self._close_menu_and_descendants(sub)
                    # clear references to the closed submenu from its owner
                    if self._active_submenu is sub:
                        self._active_submenu = None
                    try:
                        if sub._parent_menu and sub._parent_menu._active_submenu is sub:
                            sub._parent_menu._active_submenu = None
                    except: pass
            # do not consume MouseMove; allow normal processing

        # When menu(s) are visible, close the whole menu chain if user clicks outside
        if self.isVisible() and event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease):
            # get global click position (compat for Qt6/Qt5)
            pos = None
            if hasattr(event, 'globalPos'):
                try: pos = event.globalPos()
                except: pos = None
            if pos is None and hasattr(event, 'globalPosition'):
                try: pos = event.globalPosition().toPoint()
                except: pos = None

            if pos is not None:
                # check if the click is inside this menu or any of its visible submenus
                inside = self._hover_inside_menu_tree(self, pos)
                # also consider parent chain (this may be a submenu)
                p = getattr(self, '_parent_menu', None)
                while p and not inside:
                    inside = self._hover_inside_menu_tree(p, pos)
                    p = getattr(p, '_parent_menu', None)

                if not inside:
                    # close the top-most parent menu and all its descendant submenus
                    root = self
                    while getattr(root, '_parent_menu', None):
                        root = root._parent_menu

                    self._close_menu_and_descendants(root)
                    return True

        return super().eventFilter(obj, event)

    def sizeHint(self):
        fm = self.fontMetrics()
        options_max_width = 0
        # reserve icon column and submenu arrow column for all items to keep alignment consistent
        reserved_icon_w = 0
        reserved_arrow_w = 0
        items = [c for c in self._content.findChildren(ZContextItem)]
        if items:
            reserved_icon_w = max((c.iconSize().width() for c in items))
            reserved_arrow_w = max((c._drop_icon_size.width() for c in items))
        # iterate actual content children, ignoring separators for width calc
        for child in items:
            t = child.renderText()
            if t is None:
                continue
            text_w = fm.horizontalAdvance(t)
            shortcut_w = fm.horizontalAdvance(child.shortcut()) if child.shortcut() else 0
            w = text_w + shortcut_w + reserved_icon_w + reserved_arrow_w + self._content.layout().horizontalMargin() + 32
            options_max_width = max(options_max_width, w)
        content_width = options_max_width
        total_width = content_width + self._margin.horizontal()
        total_height = self._content.layout().heightHint() + self._margin.vertical()
        min_width = 100
        min_height = 30
        final_width = max(total_width, min_width)
        final_height = max(total_height, min_height)
        self.setMinimumSize(final_width, final_height)
        return QSize(final_width, final_height)

    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        m = self._margin
        rect = QRectF(self.rect()).adjusted(m.left, m.top, -m.right, -m.bottom)
        radius = self.radiusCtrl.value

        ZWidgetEffect.drawGraphicsShadow(painter, rect, radius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._content.resize(self.width() - self._margin.horizontal(), self._content.heightHint())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # click outside to close
        if not self.rect().contains(event.pos()):
            self.windowOpacityCtrl.fadeOut()

    def keyPressEvent(self, event):
        k = event.key()
        text = event.text().upper()
        # Check for mnemonic key (e.g., Alt+M for "更多(&M)")
        if text and not event.modifiers() & Qt.ControlModifier & Qt.ShiftModifier:
            for item in self._content.findChildren(ZContextItem):
                action_text = item.text()
                if action_text and '&' in action_text:
                    # Extract mnemonic character (e.g., 'M' from "更多(&M)")
                    mnemonic = action_text.split('&')[-1][0].upper() if '&' in action_text else ''
                    if mnemonic == text:
                        if item._bound_action:
                            item._bound_action.trigger()
                        return
        if k in (Qt.Key_Down, Qt.Key_Up):
            items = self._content.findChildren(ZContextItem)
            if not items:
                return
            focused = self.focusWidget()
            idx = -1
            if isinstance(focused, ZContextItem):
                try: idx = items.index(focused)
                except: idx = -1
            if k == Qt.Key_Down:
                new = 0 if idx == -1 else (idx + 1) % len(items)
            else:
                new = len(items) - 1 if idx == -1 else (idx - 1) % len(items)
            items[new].setFocus()
            return
        if k == Qt.Key_Right:
            focused = self.focusWidget()
            if isinstance(focused, ZContextItem) and focused._has_submenu:
                if focused._bound_action is not None:
                    act = focused._bound_action
                    self._open_submenu_for_item(focused, act)
            return
        if k == Qt.Key_Left and self._parent_menu:
            self.windowOpacityCtrl.fadeOut()
            try:
                self._parent_item.setFocus()
                self._parent_menu._active_submenu = None
            except: pass
            return
        if k in (Qt.Key_Return, Qt.Key_Enter):
            focused = self.focusWidget()
            if isinstance(focused, ZContextItem):
                if focused._bound_action is not None:
                    focused._bound_action.trigger()
            return
        if k == Qt.Key_Escape:
            self.windowOpacityCtrl.fadeOut()
            return
        super().keyPressEvent(event)