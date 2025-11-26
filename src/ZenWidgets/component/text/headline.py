from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt,QSize,QRectF
from PySide6.QtGui import QPainter,QFont,QFontMetrics,QPen
from ZenWidgets.component.base import (
    ZFlashEffect,
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController,
    ZWidget
)
from ZenWidgets.core import ZDebug,ZPadding
from ZenWidgets.gui import ZHeadLineColorData

class ZHeadLine(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    flashEffectCtrl: ZFlashEffect
    textColorCtrl: ZAnimatedColor
    textBackColorCtrl: ZAnimatedColor
    indicatorColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[ZHeadLineColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZHeadLine'},
        'radiusCtrl': {'value': 4.0}
    }

    def __init__(self,
                 parent: QWidget = None,
                 text: str = "",
                 font: QFont = QFont('Microsoft YaHei', 9),
                 display_indicator: bool = False,
                 indicator_is_leading: bool = False,
                 selectable: bool = False,
                 objectName: str | None = None,
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         font=font,
                         )
        if selectable: self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._text = text
        self._selected_text = ""
        self._spacing = 6
        self._indicator_width = 4
        self._isdisplay_indicator = display_indicator
        self._indicator_is_leading = indicator_is_leading
        self._padding = ZPadding(4, 4, 4, 4)
        self._alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        self._selectable = selectable
        self._selection_start = -1
        self._selection_end = -1
        self._is_selecting = False

        self._init_color_data_()
        self.setMinimumSize(self._padding.horizontal(), 24)

    # region public
    def selectedText(self) -> str: return self._selected_text

    def text(self) -> str: return self._text

    def setText(self, t: str,/,flash: bool = False) -> None:
        if flash: self.flashEffectCtrl.flash()
        self._text = t
        self.adjustSize()
        self.update()

    def isDisplayIndicator(self) -> bool: return self._isdisplay_indicator

    def setDisplayIndicator(self, v: bool) -> None:
        self._isdisplay_indicator = v
        self.adjustSize()
        self.update()

    def isIndicatorLeading(self) -> bool: return self._indicator_is_leading

    def setIndicatorLeading(self, v: bool) -> None:
        self._indicator_is_leading = v
        self.adjustSize()
        self.update()

    def isSelectable(self) -> bool: return self._selectable

    def setSelectable(self, v: bool) -> None:
        self._selectable = v
        if v: self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._clear_selection()
        self.adjustSize()
        self.update()

    def padding(self) -> ZPadding: return self._padding

    def setPadding(self, p: ZPadding) -> None:
        self._padding = p
        self.adjustSize()
        self.update()

    def spacing(self) -> int: return self._spacing

    def setSpacing(self, s: int) -> None:
        self._spacing = s
        self.adjustSize()
        self.update()

    def alignment(self) -> Qt.AlignmentFlag: return self._alignment

    def setAlignment(self, a: Qt.AlignmentFlag) -> None:
        self._alignment = a
        self.update()

    def sizeHint(self):
        p = self._padding
        fm = QFontMetrics(self.font())
        fixed_height = max(fm.height() + p.vertical(), self.minimumHeight())
        text_width = fm.horizontalAdvance(self._text) if self._text else 0
        base_width = text_width + p.horizontal()
        if self._isdisplay_indicator: base_width += self._indicator_width + self._spacing
        return QSize(max(base_width, self.minimumWidth()), fixed_height)

    def adjustSize(self):
        self.resize(self.sizeHint())

    # region private
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border
        self.textBackColorCtrl.color = data.TextBackSectcted
        self.indicatorColorCtrl.color = data.Indicator

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)
        self.textColorCtrl.setColorTo(data.Text)
        self.textBackColorCtrl.setColorTo(data.TextBackSectcted)
        self.indicatorColorCtrl.setColorTo(data.Indicator)

    def _is_selection(self) -> bool:
        return (self._selection_start != -1 and self._selection_end != -1
                and self._selection_start != self._selection_end)

    def _get_selection_range(self) -> tuple:
        return (min(self._selection_start, self._selection_end),
                max(self._selection_start, self._selection_end))

    def _update_selected_text(self):
        if self._is_selection():
            s, e = self._get_selection_range()
            self._selected_text = self._text[s:e]
        else:
            self._selected_text = ""

    def _clear_selection(self):
        self._selection_start = -1
        self._selection_end = -1
        self._is_selecting = False
        self._selected_text = ""
        self.update()

    def _get_char_position_at_point(self, point):
        """根据 x 位置返回字符索引"""
        if not self._text: return -1
        text_rect = self._get_actual_text_rect()
        fm = QFontMetrics(self.font())
        line_y = text_rect.top() + (text_rect.height() - fm.height()) / 2
        if point.y() < line_y or point.y() > line_y + fm.height(): return -1
        click_x = point.x() - text_rect.left()
        acc = 0
        for i, ch in enumerate(self._text):
            w = fm.horizontalAdvance(ch)
            if click_x <= acc + w / 2:
                return min(i, len(self._text))
            acc += w
        return len(self._text)

    def _get_actual_text_rect(self) -> QRectF:
        """计算实际的文本绘制区域（先算文字，考虑指示器占位）"""
        p = self._padding
        content_rect = self.rect().adjusted(p.left, p.top, -p.right, -p.bottom)
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self._text) if self._text else 0
        text_height = fm.height()

        indicator_offset = 0
        if self._isdisplay_indicator: indicator_offset = self._indicator_width + self._spacing

        text_x = content_rect.left() + indicator_offset
        if self._alignment & Qt.AlignmentFlag.AlignRight:
            text_x += content_rect.width() - text_width - indicator_offset
        elif self._alignment & Qt.AlignmentFlag.AlignHCenter:
            text_x += (content_rect.width() - text_width) / 2 - indicator_offset

        text_y = content_rect.top()
        if self._alignment & Qt.AlignmentFlag.AlignVCenter:
            text_y += (content_rect.height() - text_height) / 2
        elif self._alignment & Qt.AlignmentFlag.AlignBottom:
            text_y += (content_rect.height() - text_height)

        return QRectF(text_x, text_y, text_width, text_height)

    def _get_indicator_rect(self, text_rect: QRectF, fm: QFontMetrics) -> QRectF:
        """基于文字区域推导计算指示器区域"""
        indicator_w = self._indicator_width
        text_height = fm.height()
        indicator_h = max(2.0, min(text_rect.height(), text_height - fm.descent()))

        if self._indicator_is_leading:
            indicator_x = self.rect().left() + self._padding.left
        else:
            indicator_x = text_rect.left() - self._spacing - indicator_w

        if self._alignment & Qt.AlignmentFlag.AlignTop:
            indicator_y = text_rect.top()
        elif self._alignment & Qt.AlignmentFlag.AlignBottom:
            indicator_y = text_rect.bottom() - indicator_h
        else:  # AlignVCenter
            indicator_y = text_rect.center().y() - indicator_h / 2

        return QRectF(indicator_x, indicator_y, indicator_w, indicator_h)

    def _draw_selection_background(self, painter: QPainter, text_rect: QRectF, fm: QFontMetrics):
        if not (self._selectable and self._is_selection()): return
        s, e = self._get_selection_range()
        line_y = text_rect.top() + (text_rect.height() - fm.height()) / 2
        x1 = text_rect.left() + fm.horizontalAdvance(self._text[:s])
        x2 = text_rect.left() + fm.horizontalAdvance(self._text[:e])
        sel_rect = QRectF(x1, line_y + 1, max(0.0, x2 - x1), max(0.0, fm.height() - 2))
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.textBackColorCtrl.color)
        painter.drawRoundedRect(sel_rect, 2, 2)
        painter.restore()


    # region paintEvent
    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(
            QPainter.RenderHint.TextAntialiasing |
            QPainter.RenderHint.Antialiasing
        )
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value

        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        self.flashEffectCtrl.drawFlashLayer(painter, rect, radius)

        p = self._padding
        fm = self.fontMetrics()
        content_rect = rect.adjusted(p.left, p.top, -p.right, -p.bottom)

        text_rect = self._get_actual_text_rect()
        self._update_selected_text()
        if self._selectable and self._is_selection() and self._text:
            self._draw_selection_background(painter, text_rect, fm)

        painter.setFont(self.font())
        painter.setPen(self.textColorCtrl.color)
        flags = Qt.TextFlag.TextSingleLine | self._alignment
        painter.drawText(text_rect, flags, self._text)

        if self._isdisplay_indicator and self.indicatorColorCtrl.color.alpha() > 0:
            indicator_rect = self._get_indicator_rect(text_rect, fm)  # 第二步：基于文字区域算指示器
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.indicatorColorCtrl.color)
            painter.drawRoundedRect(indicator_rect, indicator_rect.width() / 2, indicator_rect.width() / 2)

        if ZDebug.draw_rect:
            ZDebug.drawRect(painter, rect)
            ZDebug.drawRect(painter, content_rect, Qt.red,penStyle=Qt.PenStyle.DashLine)
            ZDebug.drawRect(painter, text_rect, Qt.blue,penStyle=Qt.PenStyle.DashLine)
            if self._isdisplay_indicator: ZDebug.drawRect(painter, indicator_rect, Qt.green,penStyle=Qt.PenStyle.DashLine)
        event.accept()


    # region keyPressEvent
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if not self._selectable: return

        if event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if self._is_selection() and self._selected_text:
                from PySide6.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(self._selected_text)
            return

        elif event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if self._text:
                self._selection_start = 0
                self._selection_end = len(self._text)
                self.update()
            return


    # region mouseEvent
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if not self._selectable or not self._text: return

        if event.button() == Qt.MouseButton.LeftButton:
            char_pos = self._get_char_position_at_point(event.pos())
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if self._selection_start == -1:
                    self._selection_start = 0
                self._selection_end = char_pos
            else:
                self._selection_start = char_pos
                self._selection_end = char_pos
                self._is_selecting = True
                self._drag_start_pos = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self._selectable or not self._text: return

        if self._is_selecting:
            char_pos = self._get_char_position_at_point(event.pos())
            self._selection_end = char_pos
            self.update()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_selecting = False

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self._selectable: self._clear_selection()