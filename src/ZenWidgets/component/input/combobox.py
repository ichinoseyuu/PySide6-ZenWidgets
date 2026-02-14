from typing import Any,Dict,cast
from PySide6.QtGui import QPainter,QFont,QPen,QIcon,QPixmap,QColor
from PySide6.QtCore import Qt,QSize,QRect,QRectF,QPointF,Signal,Slot,QMargins,QPoint,QEvent
from PySide6.QtWidgets import QApplication,QSizePolicy
from ZenWidgets.component.layouts import ZVBoxLayout
from ZenWidgets.component.base import (
    ZOpacityEffect,
    ZFlashEffect,
    ZAnimatedColor,
    ZAnimatedOpacity,
    ZAnimatedFloat,
    ZAnimatedPointF,
    ZColorController,
    ZClickWidget,
    ZWidget,
    ZContentWidget,
    ZExclusiveToggleGroup,
    ZToggleWidget
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
class ZComboBoxItemColorData(ZColorData):
    Text: QColor
    Indicator: QColor

colordata = {
    'Light': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.Indicator: lambda: ZPalette.Primary
    },
    'Dark': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.Indicator: lambda: ZPalette.Primary
    }
}

# region ZComboBoxItem
@colordata_provider(datamap=colordata, classtype=ZComboBoxItemColorData)
class ZComboBoxItem(ZToggleWidget):
    indicatorWidth = 3
    opacityEffectCtrl: ZOpacityEffect
    radiusCtrl: ZAnimatedFloat
    textColorCtrl: ZAnimatedColor
    indicatorColorCtrl: ZAnimatedColor
    opacityCtrl: ZAnimatedOpacity
    colorDataCtrl: ZColorController[ZComboBoxItemColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZComboBoxItem'},
        'radiusCtrl': {'value': 4.0},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 text: str | None = None,
                 font=QFont("Microsoft YaHei", 9),
                 checked: bool = False,
                 objectName: str | None = None,
                 sizePolicy: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                 ):
        super().__init__(parent=parent,
                         checked=checked,
                         objectName=objectName,
                         font=font,
                         sizePolicy=sizePolicy
                         )
        self._text: str | None = text
        self._padding = ZPadding(4, 4, 16, 4)
        self._spacing = 4
        self._init_color_data_()
        self.resize(self.sizeHint())

    # region private method
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text
        self.indicatorColorCtrl.color = data.Indicator
        self.indicatorColorCtrl.opaque() if self._checked else self.indicatorColorCtrl.transparent()

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.indicatorColorCtrl.color = data.Indicator
        self.textColorCtrl.setColorTo(data.Text)
        self.indicatorColorCtrl.toOpaque() if self._checked else self.indicatorColorCtrl.toTransparent()

    def _mouse_enter_(self): self.opacityEffectCtrl.setAlphaFTo(0.11)

    def _mouse_leave_(self): self.opacityEffectCtrl.toTransparent()

    def _mouse_press_(self): self.opacityEffectCtrl.setAlphaFTo(0.16)

    def _mouse_release_(self): self.opacityEffectCtrl.setAlphaFTo(0.11)

    def _toggle_(self):
        self.opacityEffectCtrl.toTransparent()
        self.indicatorColorCtrl.toOpaque() if self._checked else self.indicatorColorCtrl.toTransparent()

    # region public method
    def text(self) -> str: return self._text

    def spacing(self) -> int: return self._spacing

    def padding(self) -> ZPadding: return self._padding

    def setText(self, t: str) -> None:
        if self._text == t: return
        self._text = t
        self.update()

    def setSpacing(self, s: int) -> None:
        if self._spacing == s: return
        self._spacing = s
        self.update()

    def setPadding(self, p: ZPadding) -> None:
        if self._padding == p: return
        self._padding = p
        self.update()

    def sizeHint(self):
        # 宽度由父控件决定，这里只计算高度
        content_height = 0
        if self._text:
            text_height = self.fontMetrics().height()
            content_height = max(content_height, text_height)
        # 加上内边距
        total_height = content_height + self._padding.top + self._padding.bottom
        # 确保最小高度
        min_height = 26
        total_height = max(total_height, min_height)
        return QSize(self.width(), total_height)

   # region event
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
        text_height = fm.height()
        indicator_w = self.indicatorWidth
        spacing = self._spacing
        content_rect = rect.adjusted(p.left, p.top, -p.right, -p.bottom)
        text_area_left = content_rect.left() + indicator_w + spacing

        if self._checked and self.indicatorColorCtrl.color.alpha() > 0:
            indicator_h = max(2.0, min(content_rect.height(), text_height - fm.descent()))
            indicator_y = content_rect.center().y() - indicator_h / 2
            indicator_x = content_rect.left()
            indicator_rect = QRectF(indicator_x, indicator_y, indicator_w, indicator_h)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.indicatorColorCtrl.color)
            painter.drawRoundedRect(indicator_rect, indicator_w / 2, indicator_w / 2)

        if self._text:
            text_rect = QRect(
                text_area_left,
                content_rect.top(),
                content_rect.width() - (text_area_left - content_rect.left()),
                content_rect.height()
            )
            painter.setFont(self.font())
            painter.setPen(self.textColorCtrl.color)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self._text)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()


class ZComboBoxViewColorData(ZColorData):
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

# region ZComboBoxView
@colordata_provider(datamap=colordata_2, classtype=ZComboBoxViewColorData)
class ZComboBoxView(ZWidget):
    selected = Signal(str)

    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZComboBoxViewColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZComboBoxView'},
        'radiusCtrl': {'value': 5.0},
    }
    def __init__(self, parent: ZWidget | None = None, items: list[str] = None):
        super().__init__(parent=parent,f=Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._margin = ZMargins(8, 8, 8, 8)
        self._content = ZContentWidget(self)
        self._content.setLayout(ZVBoxLayout(self, margins=QMargins(4, 4, 4, 4), spacing=2))
        self._content.move(self._margin.left, self._margin.top)
        self._items: list[str] = items
        self._item_group = ZExclusiveToggleGroup(self)
        self._item_group.toggled.connect(self._item_toggle_handler_)
        self.windowOpacityCtrl.completelyHide.connect(self.hide)
        self._init_color_data_()
        self._init_items_()

    # region private method
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)

    def _init_items_(self):
        if not self._items:
            self._items = []
            return
        for text in self._items:
            item = ZComboBoxItem(self, text=text)
            self._content.addWidget(item)
            self._item_group.addWidget(item)
        self.resize(self.sizeHint())

    def _item_toggle_handler_(self):
        checked_item = cast(ZComboBoxItem, self._item_group.checkedWidget())
        self.selected.emit(checked_item._text)
        self.windowOpacityCtrl.fadeOut()

    def _get_top_left_position_(self) -> QPoint:
        target = self.parentWidget()
        checked_item = self._item_group.checkedWidget()
        offset = self._margin.topLeft() + QPoint(ZComboBoxItem.indicatorWidth, 0)
        if not checked_item: return target.mapToGlobal(target.rect().bottomLeft()) - offset
        offset += QPoint(0, (target.height() + checked_item.height())//2-target.height())
        parent_pos = target.mapToGlobal(target.rect().topLeft())
        return parent_pos - checked_item.geometry().topLeft() - offset

    # region public method
    def addItem(self, text: str):
        item = ZComboBoxItem(self, text=text)
        self._content.layout().addWidget(item)
        self._item_group.addWidget(item, set_first_checked=False)
        self._items.append(text)
        self.resize(self.sizeHint())

    def addItems(self, texts: list[str]):
        for text in texts:
            item = ZComboBoxItem(self, text=text)
            self._content.layout().addWidget(item)
            self._item_group.addWidget(item, set_first_checked=False)
            self._items.append(text)
        self.resize(self.sizeHint())

    def removeItem(self, text: str):
        for item in self._item_group.widgets():
            item = cast(ZComboBoxItem, item)
            if item.text() == text:
                self._items.remove(text)
                item.clicked.disconnect()
                item.deleteLater()
                self._item_group.removeWidget(item)
                self._content.layout().removeWidget(item)
                break
        self.resize(self.sizeHint())

    def toggleTo(self, text: str):
        for item in self._item_group.widgets():
            item = cast(ZComboBoxItem, item)
            if item.text() == text:
                try:self._item_group.checkedWidget().setChecked(False)
                except:pass
                item.setChecked(True)
                break

    def show(self):
        QApplication.instance().installEventFilter(self)
        super().show()
        self.move(self._get_top_left_position_())
        self.widgetSizeCtrl.resizeFromTo(QSize(self.widthHint(),0),self.sizeHint())
        self.setFocus(Qt.FocusReason.PopupFocusReason)
        self.activateWindow()
        self.raise_()

    def hide(self):
        QApplication.instance().removeEventFilter(self)
        super().hide()

    def eventFilter(self, obj, event):
        if self.isVisible() and event.type() == QEvent.Type.Wheel:
            return True
        return super().eventFilter(obj, event)

    def sizeHint(self): return QSize(self.parentWidget().widthHint() + self._content.layout().horizontalMargin(), self._content.layout().heightHint()) + self._margin.size()

    # region event
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._content.resize(self.width() - self._margin.horizontal(), self._content.heightHint())

    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        m = self._margin
        rect = QRectF(self.rect()).adjusted(m.left, m.top, -m.right, -m.bottom)
        radius = self.radiusCtrl.value

        ZWidgetEffect.drawGraphicsShadow(painter, rect, radius)

        # 再绘制背景与边框
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.windowOpacityCtrl.fadeIn()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.windowOpacityCtrl.fadeOut()

class ZComboBoxColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    Icon: QColor

colordata_3 = {
    'Light': {
        ZColorDataKey.Body: lambda: ZPalette.Body,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.Icon: lambda: ZPalette.Icon
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.Body,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.Icon: lambda: ZPalette.Icon
    }
}

# region ZComboBox
@colordata_provider(datamap=colordata_3, classtype=ZComboBoxColorData)
class ZComboBox(ZClickWidget):
    optionChanged = Signal(str, object)
    '''选项改变信号'''

    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    opacityLayerCtrl: ZOpacityEffect
    flashLayerCtrl: ZFlashEffect
    textColorCtrl: ZAnimatedColor
    dropIconColorCtrl: ZAnimatedColor
    dropIconPosCtrl: ZAnimatedPointF
    colorDataCtrl: ZColorController[ZComboBoxColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZComboBox'},
        'radiusCtrl': {'value': 4.0},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 options: Dict[str, Any]= None,
                 text: str = None,
                 font: QFont = QFont("Microsoft YaHei", 9),
                 objectName: str | None = None
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         font=font,
                         focusPolicy=Qt.FocusPolicy.ClickFocus
                         )
        self._options: Dict[str, Any] = {}
        self._text: str = None
        self._drop_icon: QIcon = ZGlobal.getBuiltinIcon(u':/icons/arrow_down.svg')
        self._drop_icon_size = QSize(12, 12)
        self._padding = ZPadding(8, 8, 8, 8)
        self._spacing: int = 16
        if text :self._text = text
        if options: self._options = options
        self._options_view = ZComboBoxView(self, self._options.keys())
        self._options_view.selected.connect(self._select_handler_)

        self.dropIconPosCtrl.animation.setBias(0.1)
        self.dropIconPosCtrl.animation.setFactor(0.2)
        self._init_color_data_()
        self.resize(self.sizeHint())
        self.dropIconPosCtrl.setPos(self._get_drop_icon_pos())

    # region private method
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border
        self.dropIconColorCtrl.color = data.Icon
        self.textColorCtrl.color = data.Text

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)
        self.dropIconColorCtrl.setColorTo(data.Icon)
        self.textColorCtrl.setColorTo(data.Text)

    def _mouse_enter_(self): self.opacityLayerCtrl.setAlphaFTo(0.06)

    def _mouse_leave_(self): self.opacityLayerCtrl.toTransparent()

    def _mouse_press_(self):
        self.opacityLayerCtrl.setAlphaFTo(0.11)
        self.dropIconPosCtrl.moveBy(0, 2)

    def _mouse_release_(self):
        self.opacityLayerCtrl.setAlphaFTo(0.06)
        self.dropIconPosCtrl.moveTo(self._get_drop_icon_pos())

    def _mouse_click_(self): self._options_view.show()

    @Slot(str)
    def _select_handler_(self, item: str):
        '''选项选择处理'''
        self.flashLayerCtrl.flash(0.3)
        if item in self._options:
            self._text = item
            self.optionChanged.emit(item, self._options[item])
            self.update()

    def _get_drop_icon_pos(self):
        '''获取下拉图标位置'''
        rect = self.rect()
        icon_x = rect.right() - self._drop_icon_size.width() - self._padding.right
        icon_y = (rect.height() - self._drop_icon_size.height()) // 2 + 1
        return QPointF(icon_x, icon_y)

    # region public method
    def options(self) -> list[str]: return list(self._options.keys())

    def currentValue(self) -> Any | None: return self._options[self._text] if self._text in self._options else None

    def text(self) -> str: return self._text

    def icon(self) -> QIcon: return QIcon(self._icon)

    def iconSize(self) -> QSize: return QSize(self._icon_size)

    def spacing(self) -> int: return self._spacing

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

    def addOption(self, k: str, v: Any = None) -> None:
        #self._options.append(item) # ZItemView 内部的items 与 _options 共用内存
        self._options[k] = v
        self._options_view.addItem(k)
        # if key == self._text:
        #     self._options_view.selectItem(key)
        self.adjustSize()

    def addOptions(self, o: Dict[str, Any]| list[tuple[str, Any]]| list[str]) -> None:
        if isinstance(o, dict):
            self._options.update(o)
            self._options_view.addItems(o.keys())
        elif isinstance(o, list):
            for item in o:
                if isinstance(item, str):
                    self.addOption(item)
                elif isinstance(item, tuple):
                    self.addOption(item[0], item[1])
        else:
            raise TypeError(f'addOptions({o}) type error')
        self.adjustSize()

    def removeOption(self, key: str) -> None:
        if key in self._options:
            del self._options[key]
            self._options_view.removeItem(key)
            if self._text == key:
                self._text = None
        self.adjustSize()

    def toggleTo(self, key: str) -> None: self._options_view.toggleTo(key)

    def adjustSize(self): self.resize(self.sizeHint()); self.dropIconPosCtrl.setPos(self._get_drop_icon_pos())

    def sizeHint(self):
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text) if self._text else 0
        options_max_width = 0
        for k in self._options.keys():
            if k is None:
                continue
            w = fm.horizontalAdvance(k)
            if w > options_max_width:
                options_max_width = w
        content_width = max(text_width, options_max_width)
        total_width = content_width + self._drop_icon_size.width() + self._padding.horizontal() + self._spacing
        font_height = self.fontMetrics().height()
        total_height = max(font_height + self._padding.vertical(), self._drop_icon_size.height() + 2)
        min_width = 100
        min_height = 30
        final_width = max(total_width, min_width)
        final_height = max(total_height, min_height)
        self.setMinimumSize(final_width, final_height)
        return QSize(final_width, final_height)

    # region event
    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing|
            QPainter.RenderHint.TextAntialiasing|
            QPainter.RenderHint.SmoothPixmapTransform
            )
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value

        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        self.opacityLayerCtrl.drawOpacityLayer(painter, rect, radius)
        self.flashLayerCtrl.drawFlashLayer(painter, rect, radius)

        if self._text:
            painter.setFont(self.font())
            painter.setPen(self.textColorCtrl.color)
            painter.drawText(
                rect.adjusted(self._padding.left, 0, 0, 0),
                Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter,
                self._text
                )

        pixmap = self._drop_icon.pixmap(self._drop_icon_size)
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.setDevicePixelRatio(self.devicePixelRatioF())
        colored_pixmap.fill(Qt.GlobalColor.transparent)
        painter_pix = QPainter(colored_pixmap)
        painter_pix.drawPixmap(0, 0, pixmap)
        painter_pix.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter_pix.fillRect(colored_pixmap.rect(), self.dropIconColorCtrl.color)
        painter_pix.end()
        painter.drawPixmap(self.dropIconPosCtrl.pos, colored_pixmap)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()