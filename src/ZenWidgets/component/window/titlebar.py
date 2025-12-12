from PySide6.QtCore import QEvent,Qt,QLineF,QPoint,QPointF,QSize
from PySide6.QtGui import QPainter,QPen,QColor,QPainterPath,QIcon,QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget
from ZenWidgets.component.window.win32utils import startSystemMove,toggleWindowState
from ZenWidgets.component.base.widget import ClickInteractiveWidget
from ZenWidgets.component.base.controller import ZAnimatedColor,ZColorController
from ZenWidgets.component.text import ZHeadLine
from ZenWidgets.core import ZDebug,ZGlobal,ZPosition
from ZenWidgets.gui import ZTitleBarButtonColorData,ZTheme

__all__ = [
    'ZTitleBarButton',
    'CloseButton',
    'MaximizeButton',
    'MinimizeButton',
    'ToggleThemeButton',
    'ZTitleBarBase',
    'ZTitleBar'
]

# region ZTitleBarButton
class ZTitleBarButton(ClickInteractiveWidget):
    bodyColorCtrl: ZAnimatedColor
    iconColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[ZTitleBarButtonColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl': {'key': 'ZTitleBarButton'}
        }
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_NoMousePropagation) # 防止鼠标事件传播到父组件
        self.setFixedSize(46, 32)

    def _init_color_data_(self):
        self.bodyColorCtrl.setColor(QColor(140, 140, 140, 0))
        self.iconColorCtrl.color = self.colorDataCtrl.data.Icon

    def _color_data_change_handler_(self): self.iconColorCtrl.setColorTo(self.colorDataCtrl.data.Icon)

    def _show_tooltip_(self):
        if self.toolTip() != '':
            ZGlobal.tooltip.showTip(
                text=self.toolTip(),
                target=self,
                mode=ZGlobal.tooltip.Mode.TrackTarget,
                position=ZPosition.Bottom,
                offset=QPoint(6, 6)
                )

    def _hide_tooltip_(self):
        if self.toolTip() != '': ZGlobal.tooltip.hideTip()

    def enterEvent(self, event):
        super().enterEvent(event)
        self._show_tooltip_()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hide_tooltip_()

# region CloseButton
class CloseButton(ZTitleBarButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_color_data_()

    def _init_color_data_(self):
        self.bodyColorCtrl.setColor(QColor('#00E81B23'))
        self.iconColorCtrl.color = self.colorDataCtrl.data.Icon

    def _mouse_enter_(self):
        self.bodyColorCtrl.setAlphaFTo(1.0)
        self.iconColorCtrl.setColorTo(QColor('#F2F2F2'))

    def _mouse_leave_(self):
        self.bodyColorCtrl.toTransparent()
        self.iconColorCtrl.setColorTo(self.colorDataCtrl.data.Icon)

    def _mouse_press_(self): self.bodyColorCtrl.setAlphaFTo(0.6)

    def _mouse_release_(self): self.bodyColorCtrl.setAlphaFTo(1.0)

    def paintEvent(self, e):
        painter = QPainter(self)

        painter.setBrush(self.bodyColorCtrl.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect().adjusted(0, 1, -1, 0))

        painter.save()
        r =self.devicePixelRatioF()
        pen = QPen(self.iconColorCtrl.color, 1.2 * 1/r)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        w, h = self.width(), self.height()
        iw = ih = 10
        x = w/2 - iw/2
        y = h/2 - ih/2
        lines = [
            QLineF(x, y, x + iw, y + ih),
            QLineF(x + iw, y, x, y + ih)
        ]
        painter.drawLines(lines)
        painter.restore()

        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        e.accept()

# region MaximizeButton
class MaximizeButton(ZTitleBarButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_color_data_()

    def _mouse_enter_(self): self.bodyColorCtrl.setAlphaFTo(0.2)

    def _mouse_leave_(self): self.bodyColorCtrl.toTransparent()

    def _mouse_press_(self): self.bodyColorCtrl.setAlphaFTo(0.4)

    def _mouse_release_(self): self.bodyColorCtrl.setAlphaFTo(0.2)

    def paintEvent(self, e):
        painter = QPainter(self)

        painter.setBrush(self.bodyColorCtrl.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect().adjusted(0, 1, 0, 0))

        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(self.iconColorCtrl.color, 1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        r = self.devicePixelRatioF()
        painter.scale(1/r, 1/r)
        if not self.window().isMaximized():
            painter.drawRect(int(18*r), int(11*r), int(10*r), int(10*r))
        else:
            painter.drawRect(int(18*r), int(13*r), int(8*r), int(8*r))
            x0 = int(18*r)+int(2*r)
            y0 = 13*r
            dw = int(2*r)
            path = QPainterPath(QPointF(x0, y0))
            path.lineTo(x0, y0-dw)
            path.lineTo(x0+8*r, y0-dw)
            path.lineTo(x0+8*r, y0-dw+8*r)
            path.lineTo(x0+8*r-dw, y0-dw+8*r)
            painter.drawPath(path)
        painter.restore()

        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        e.accept()

# region MinimizeButton
class MinimizeButton(ZTitleBarButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_color_data_()

    def _mouse_enter_(self): self.bodyColorCtrl.setAlphaFTo(0.2)

    def _mouse_leave_(self): self.bodyColorCtrl.toTransparent()

    def _mouse_press_(self): self.bodyColorCtrl.setAlphaFTo(0.4)

    def _mouse_release_(self): self.bodyColorCtrl.setAlphaFTo(0.2)

    def paintEvent(self, e):
        painter = QPainter(self)

        painter.setBrush(self.bodyColorCtrl.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect().adjusted(0, 1, 0, 0))

        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(self.iconColorCtrl.color, 1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLine(18, 16, 28, 16)
        painter.restore()

        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        e.accept()


# region ToggleThemeButton
class ToggleThemeButton(ZTitleBarButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        icon = QIcon()
        icon.addPixmap(
            ZGlobal.iconPack.toPixmap("ic_fluent_weather_moon_filled"),
            state=QIcon.State.Off
        )
        icon.addPixmap(
            ZGlobal.iconPack.toPixmap("ic_fluent_weather_sunny_filled"),
            state=QIcon.State.On
        )
        self._icon: QIcon = icon
        self._icon_size: QSize = QSize(16, 16)
        self._init_color_data_()

    def _mouse_enter_(self): self.bodyColorCtrl.setAlphaFTo(0.2)

    def _mouse_leave_(self): self.bodyColorCtrl.toTransparent()

    def _mouse_press_(self): self.bodyColorCtrl.setAlphaFTo(0.4)

    def _mouse_release_(self): self.bodyColorCtrl.setAlphaFTo(0.2)

    def _mouse_click_(self): ZGlobal.themeManager.toggleTheme()

    def paintEvent(self, e):
        painter = QPainter(self)
        #painter.setRenderHints(QPainter.RenderHint.Antialiasing|QPainter.RenderHint.SmoothPixmapTransform)
        painter.setBrush(self.bodyColorCtrl.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect().adjusted(0, 1, 0, 0))
        icon_size = self._icon_size
        is_dark = ZGlobal.themeManager.getTheme() is ZTheme.Dark
        pixmap = self._icon.pixmap(icon_size, state=QIcon.State.On if is_dark else QIcon.State.Off)
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.setDevicePixelRatio(self.devicePixelRatioF())
        colored_pixmap.fill(Qt.transparent)
        painter_pix = QPainter(colored_pixmap)
        painter_pix.drawPixmap(0, 0, pixmap)
        painter_pix.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter_pix.fillRect(colored_pixmap.rect(), self.iconColorCtrl.color)
        painter_pix.end()
        painter.drawPixmap((46 - icon_size.width()) // 2,(32 - icon_size.height()) // 2,colored_pixmap)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        e.accept()

# region ZTitleBarBase
class ZTitleBarBase(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self._isDoubleClickEnabled = True
        self._moved = False
        self.dragPosition: QPoint = None
        self.setFixedHeight(32)
        self.themeBtn = ToggleThemeButton(parent=self)
        self.minBtn = MinimizeButton(parent=self)
        self.maxBtn = MaximizeButton(parent=self)
        self.closeBtn = CloseButton(parent=self)
        self.minBtn.clicked.connect(self.window().showMinimized)
        self.maxBtn.clicked.connect(self._toggleMaxState)
        self.closeBtn.clicked.connect(self.window().close)
        self.window().installEventFilter(self)

    def _toggleMaxState(self):
        toggleWindowState(self.window())
        self._releaseMouseLeftButton()

    def _releaseMouseLeftButton(self):
        from .win32utils import releaseMouseLeftButton
        releaseMouseLeftButton(self.window().winId())

    def _isDragRegion(self, pos):
        width = 0
        for button in self.findChildren(ZTitleBarButton):
            if button.isVisible():
                width += button.width()

        return 0 < pos.x() < self.width() - width

    def _hasButtonPressed(self):
        return any(btn.isPressed() for btn in self.findChildren(ZTitleBarButton))

    def canDrag(self, pos):
        return self._isDragRegion(pos) and not self._hasButtonPressed()

    def setDoubleClickEnabled(self, isEnabled):
        self._isDoubleClickEnabled = isEnabled

    def eventFilter(self, obj, event):
        if obj is self.window():
            if event.type() == QEvent.Type.WindowStateChange:
                self.maxBtn.update()
                return False
        return super().eventFilter(obj, event)

    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or not self._isDoubleClickEnabled: return
        self._toggleMaxState()

    def mouseMoveEvent(self, event):
        if not self.canDrag(event.pos()): return
        startSystemMove(self.window())

    def mousePressEvent(self, event):
        if not self.canDrag(event.pos()): return

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()

# region ZTitleBar
class ZTitleBar(ZTitleBarBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.themeBtn, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addWidget(self.minBtn, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addWidget(self.maxBtn, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.addWidget(self.closeBtn, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(0, 0)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self.iconLabel, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.window().windowIconChanged.connect(self.setIcon)

        self.title = ZHeadLine(self)
        self.hBoxLayout.insertWidget(2, self.title, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.title.setText(title)

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(20, 20))
        self.iconLabel.setFixedSize(20, 20)

    def setIconVisible(self, v: bool):
        self.iconLabel.setVisible(v)

    def setThemeBtnVisible(self, v: bool):
        self.themeBtn.setVisible(v)

    def setMaxBtnVisible(self, v: bool):
        self.maxBtn.setVisible(v)