from typing import overload
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QMargins, Slot, QPoint, QSize, QRect, QRectF,Signal
from PySide6.QtGui import QMouseEvent, QPainter, QIcon , QPixmap, QColor
from ZenWidgets.component.layouts import ZVBoxLayout
from ZenWidgets.component.base import (
    ZOpacityEffect,
    ZAnimatedColor,
    ZAnimatedOpacity,
    ZAnimatedFloat,
    ZColorController,
    ZExclusiveToggleGroup,
    ZWidget,
    ClickInteractiveWidget,
    ToggleInteractiveWidget
)
from ZenWidgets.core import (
    ZDebug,
    ZDebug,
    ZGlobal,
    ZPosition
)
from ZenWidgets.gui import (
    ZNavigationBarColorData,
    ZNavBarButtonColorData,
    ZNavBarToggleButtonColorData,
)

# region ZNavBarButton
class ZNavBarButton(ClickInteractiveWidget):
    opacityEffectCtrl: ZOpacityEffect
    iconColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    opacityCtrl: ZAnimatedOpacity
    colorDataCtrl: ZColorController[ZNavBarButtonColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZNavBarButton'},
        'radiusCtrl': {'value': 5.0},
    }

    def __init__(self,
                 parent: ZWidget | QWidget | None = None,
                 icon: QIcon | None = None,
                 fixed_size: QSize = QSize(40, 40),
                 objectName: str | None = None,
                 toolTip: str | None = None,
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         toolTip=toolTip
                         )
        self._icon: QIcon = icon
        self._icon_size = QSize(20, 20)
        self._init_color_data_()
        self.setFixedSize(fixed_size)

    # private method
    def _init_color_data_(self):
        self.iconColorCtrl.color = self.colorDataCtrl.data.Icon

    def _color_data_change_handler_(self):
        self.iconColorCtrl.setColorTo(self.colorDataCtrl.data.Icon)

    def _show_tooltip_(self):
        if self.toolTip() != '':
            ZGlobal.tooltip.showTip(
                text = self.toolTip(),
                target = self,
                mode = ZGlobal.tooltip.Mode.TrackTarget,
                position = ZPosition.Right,
                offset = QPoint(10, 0)
                )

    def _hide_tooltip_(self):
        if self.toolTip() != '': ZGlobal.tooltip.hideTip()

    def _mouse_enter_(self): self.opacityEffectCtrl.setAlphaFTo(0.08)

    def _mouse_leave_(self): self.opacityEffectCtrl.toTransparent()

    def _mouse_press_(self): self.opacityEffectCtrl.setAlphaFTo(0.16)

    def _mouse_release_(self): self.opacityEffectCtrl.setAlphaFTo(0.08)

    # public method
    def icon(self) -> QIcon: return QIcon(self._icon)

    def iconSize(self) -> QSize: return QSize(self._icon_size)

    def setIcon(self, i: QIcon) -> None: self._icon = i; self.update()

    def setIconSize(self, s: QSize) -> None:
        if self._icon_size == s: return
        self._icon_size = s
        self.update()

    # event
    def enterEvent(self, event):
        super().enterEvent(event)
        self._show_tooltip_()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hide_tooltip_()

    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing|
            QPainter.RenderHint.SmoothPixmapTransform
            )
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value
        if self.opacityEffectCtrl.color.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.opacityEffectCtrl.color)
            painter.drawRoundedRect(rect, radius, radius)
        pixmap = self._icon.pixmap(self._icon_size)
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.setDevicePixelRatio(self.devicePixelRatioF())
        colored_pixmap.fill(Qt.transparent)
        painter_pix = QPainter(colored_pixmap)
        painter_pix.drawPixmap(0, 0, pixmap)
        painter_pix.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter_pix.fillRect(colored_pixmap.rect(), self.iconColorCtrl.color)
        painter_pix.end()
        icon_x = (self.width() - self._icon_size.width()) // 2
        icon_y = (self.height() - self._icon_size.height()) // 2
        painter.drawPixmap(icon_x, icon_y, colored_pixmap)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()

# region ZNavBarToggleButton
class ZNavBarToggleButton(ToggleInteractiveWidget):
    opacityEffectCtrl: ZOpacityEffect
    iconColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    opacityCtrl: ZAnimatedOpacity
    colorDataCtrl: ZColorController[ZNavBarToggleButtonColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZNavBarToggleButton'},
        'radiusCtrl': {'value': 5.0},
    }
    def __init__(self,
                 parent: ZWidget | QWidget | None = None,
                 icon: QIcon | None = None,
                 fixed_size: QSize = QSize(40, 40),
                 objectName: str | None = None,
                 toolTip: str | None = None,
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         toolTip=toolTip,
                         )
        self.setButtonGroup(True)
        self._icon = icon
        self._icon_size = QSize(20, 20)
        self._init_color_data_()
        self.setFixedSize(fixed_size)

    # private method
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        if self._checked:
            self.opacityEffectCtrl.setAlphaF(0.1)
            self.iconColorCtrl.color = data.IconToggled
        else:
            self.iconColorCtrl.color = data.Icon

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        if self._checked:
            self.iconColorCtrl.setColorTo(data.IconToggled)
        else:
            self.iconColorCtrl.setColorTo(data.Icon)

    def _show_tooltip_(self):
        if self.toolTip() != '':
            ZGlobal.tooltip.showTip(
                text = self.toolTip(),
                target = self,
                mode = ZGlobal.tooltip.Mode.TrackTarget,
                position = ZPosition.Right,
                offset = QPoint(10, 0)
                )

    def _hide_tooltip_(self):
        if self.toolTip() != '': ZGlobal.tooltip.hideTip()

    def _mouse_enter_(self): self.opacityEffectCtrl.setAlphaFTo(0.12 if self._checked else 0.08)

    def _mouse_leave_(self): self.opacityEffectCtrl.setAlphaFTo(0.1 if self._checked else .0)

    def _mouse_press_(self): self.opacityEffectCtrl.setAlphaFTo(0.18 if self._checked else 0.16)

    def _mouse_release_(self): self.opacityEffectCtrl.setAlphaFTo(0.08)

    def _button_toggle_(self):
        data = self.colorDataCtrl.data
        if self._checked:
            self.opacityEffectCtrl.setAlphaFTo(0.12)
            self.iconColorCtrl.setColorTo(data.IconToggled)
        else:
            self.opacityEffectCtrl.setAlphaFTo(0.08)
            self.iconColorCtrl.setColorTo(data.Icon)

    # private method
    def icon(self) -> QIcon: return QIcon(self._icon)

    def iconSize(self) -> QSize: return QSize(self._icon_size)

    def setIcon(self, i: QIcon) -> None: self._icon = i; self.update()

    def setIconSize(self, s: QSize) -> None:
        if self._icon_size == s: return
        self._icon_size = s
        self.update()

    # event
    def enterEvent(self, event):
        super().enterEvent(event)
        self._show_tooltip_()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hide_tooltip_()

    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing|
            QPainter.RenderHint.SmoothPixmapTransform
            )
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value
        if self.opacityEffectCtrl.color.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self.opacityEffectCtrl.color)
            painter.drawRoundedRect(rect, radius, radius)
        if self._checked:
            pixmap = self._icon.pixmap(self._icon_size, QIcon.Mode.Normal, QIcon.State.On)
        else:
            pixmap = self._icon.pixmap(self._icon_size, QIcon.Mode.Normal, QIcon.State.Off)
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.setDevicePixelRatio(self.devicePixelRatioF())
        colored_pixmap.fill(Qt.transparent)
        painter_pix = QPainter(colored_pixmap)
        painter_pix.drawPixmap(0, 0, pixmap)
        painter_pix.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter_pix.fillRect(colored_pixmap.rect(), self.iconColorCtrl.color)
        painter_pix.end()
        icon_x = (self.width() - self._icon_size.width()) // 2
        icon_y = (self.height() - self._icon_size.height()) // 2
        painter.drawPixmap(icon_x, icon_y, colored_pixmap)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()


# region Panel
class Panel(QWidget):
    wheeled: Signal = Signal()
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._content = QWidget(self)
        self._content.setLayout(ZVBoxLayout(self._content,QMargins(0, 0, 0, 0),6,Qt.AlignTop|Qt.AlignHCenter))
        self._offset = 0

    def _updateContentGeometry(self):
        content_height = self._content.layout().sizeHint().height()
        self._content.resize(self.width(), content_height)
        self._content.move(0, -self._offset)

    def layout(self) -> ZVBoxLayout:
        return self._content.layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._updateContentGeometry()

    def wheelEvent(self, event: QMouseEvent):
        content_height = self._content.layout().sizeHint().height()
        visible_height = self.height()
        if content_height <= visible_height:
            return

        max_offset = max(0, content_height - visible_height)
        delta = event.angleDelta().y()
        step = 30
        if delta < 0:
            self._offset = min(self._offset + step, max_offset)
        elif delta > 0:
            self._offset = max(self._offset - step, 0)
        self._updateContentGeometry()
        self.wheeled.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()

# region FooterPanel
class FooterPanel(QWidget):
    def __init__(self,parent: QWidget = None):
        super().__init__(parent)
        self.setLayout(ZVBoxLayout(self,QMargins(0, 0, 0, 0),6,Qt.AlignBottom|Qt.AlignHCenter))

    def layout(self) -> ZVBoxLayout:
        return super().layout()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()

# region Indicator
class Indicator(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    opacityCtrl: ZAnimatedOpacity

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        radius = self.width() / 2
        if self.bodyColorCtrl.color.alpha() > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.bodyColorCtrl.color)
            painter.drawRoundedRect(rect, radius, radius)
        event.accept()

# region ZNavigationBar
class ZNavigationBar(ZWidget):
    colorDataCtrl: ZColorController[ZNavigationBarColorData]
    __controllers_kwargs__ = {'colorDataCtrl':{'key': 'ZNavigationBar'}}

    def __init__(self,
                 parent: QWidget | ZWidget | None = None,
                 btn_size: QSize = QSize(40, 40),
                 btn_icon_size: QSize = QSize(20, 20),
                 objectName: str | None = None
                 ):
        super().__init__(parent=parent,
                         objectName=objectName
                         )
        self._buttons: list[ZNavBarButton|ZNavBarToggleButton] = []
        self._button_map: dict[str, ZNavBarButton|ZNavBarToggleButton] = {}
        self._btn_size = btn_size
        self._btn_icon_size = btn_icon_size
        self._panel = Panel(self)
        self._footer_panel = FooterPanel(self)
        self._indicator = Indicator(self)
        self._indicator.setFixedWidth(3)
        self.setLayout(ZVBoxLayout(self, margins=QMargins(0, 0, 0, 0), spacing=0))
        self.layout().addWidget(self._panel, stretch=1)
        self.layout().addWidget(self._footer_panel, stretch=0)
        self._btn_manager = ZExclusiveToggleGroup()
        self._btn_manager.toggled.connect(self._update_indicator_)
        self._panel.wheeled.connect(self._sync_indicator_)
        self._init_color_data_()

    # region public
    def panel(self) -> Panel:
        return self._panel

    def footerPanel(self) -> FooterPanel:
        return self._footer_panel

    def btnSize(self) -> QSize:return self._btn_size

    def setBtnSize(self, size: QSize) -> None:
        self._btn_size = size
        for btn in self.getAllButtons():
            btn.setFixedSize(size)

    def btnIconSize(self) -> QSize:return self._btn_icon_size

    def setBtnIconSize(self, size: QSize) -> None:
        self._btn_icon_size = size
        for btn in self.getAllButtons():
            btn.setIconSize(size)

    @overload
    def getButton(self, index: int) -> ZNavBarButton|ZNavBarToggleButton: ...

    @overload
    def getButton(self, name: str) -> ZNavBarButton|ZNavBarToggleButton: ...

    def getButton(self, arg) -> ZNavBarButton|ZNavBarToggleButton:
        if isinstance(arg, int):
            return self._buttons[arg]
        elif isinstance(arg, str):
            return self._button_map[arg]

    def getAllButtons(self) -> list[ZNavBarButton|ZNavBarToggleButton]:
        return [btn for (name, btn) in self._buttons]

    def addButton(self, name: str, icon: QIcon, panel: Panel|FooterPanel, tooltip: str = None):
        btn = ZNavBarButton(panel, objectName=name, icon=icon, fixed_size=self._btn_size, toolTip=tooltip)
        panel.layout().addWidget(btn)
        self._buttons.append(btn)
        self._button_map[name] = btn

    def insertButton(self, name: str, icon: QIcon, index: int, panel: Panel|FooterPanel, tooltip: str = None):
        btn = ZNavBarButton(panel, objectName=name, icon=icon, fixed_size=self._btn_size, toolTip=tooltip)
        panel.layout().insertWidget(index, btn)
        self._button_map[name] = btn
        if panel is self._footer_panel:
            index += self._panel.layout().count()
        self._buttons.insert(index, btn)

    def addToggleButton(self, name: str, icon: QIcon, panel: Panel|FooterPanel, tooltip: str = None):
        btn = ZNavBarToggleButton(panel, objectName=name, icon=icon, fixed_size=self._btn_size, toolTip=tooltip)
        panel.layout().addWidget(btn)
        self._btn_manager.addWidget(btn)
        self._buttons.append(btn)
        self._button_map[name] = btn

    def insertToggleButton(self, name: str, icon: QIcon, index: int, panel: Panel|FooterPanel, tooltip: str = None):
        btn = ZNavBarToggleButton(panel, objectName=name, icon=icon, fixed_size=self._btn_size, toolTip=tooltip)
        panel.layout().insertWidget(index, btn)
        self._button_map[name] = btn
        if panel is self._footer_panel:
            index += self._panel.layout().count()
        self._buttons.insert(index, btn)

    def toggleToNextButton(self):
        self._btn_manager.toggleToNext()

    def toggleToLastButton(self):
        self._btn_manager.toggleToLast()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()

    # region private
    def _init_color_data_(self):
        self._indicator.resize(3, self._btn_size.height()-20)
        self._indicator.bodyColorCtrl.color = self.colorDataCtrl.data.Indicator

    def _color_data_change_handler_(self):
        self._indicator.bodyColorCtrl.setColorTo(self.colorDataCtrl.data.Indicator)

    @Slot()
    def _update_indicator_(self):
        btn = self._btn_manager.checkedWidget()
        current_pos = self._indicator.pos()
        target_pos = self._get_btn_global_pos_(btn)
        distance = abs(target_pos.y() - current_pos.y())
        factor = min(0.5, max(0.2, distance / btn.height()))
        self._indicator.widgetPositionCtrl.animation.setFactor(factor)
        self._indicator.widgetPositionCtrl.moveTo(
            target_pos.x(),
            target_pos.y() + (btn.height()-self._indicator.height())//2
            )

    @Slot()
    def _sync_indicator_(self):
        btn = self._btn_manager.checkedWidget()
        if btn.parentWidget() is self._panel:
            self._indicator.stackUnder(self._footer_panel)
        else:
            self._indicator.raise_()
        target_pos = self._get_btn_global_pos_(btn)
        self._indicator.move(
            target_pos.x(),
            target_pos.y() + (btn.height()-self._indicator.height())//2
            )

    def _get_btn_global_pos_(self, btn: ZNavBarButton|ZNavBarToggleButton) -> QPoint:
        return btn.pos() + btn.parentWidget().pos()