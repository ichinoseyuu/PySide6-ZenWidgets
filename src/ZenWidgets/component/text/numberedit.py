from ast import arg
import logging
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import Signal,QSize,QTimer,QPoint,QPointF,QRectF,Qt
from PySide6.QtGui import QFontMetrics,QFont,QWheelEvent,QMouseEvent,QPainterPath,QPainter,QKeyEvent,QPen,QColor
from ZenWidgets.component.base import (
    ZOpacityEffect,
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController,
    ZWidget
)
from ZenWidgets.core import ZDebug,ZPadding,ZTextSnapshot

from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

class ZNumberEditColorData(ZColorData):
    Body: QColor
    BodyFocused: QColor
    Border: QColor
    Text: QColor
    TextBackSectcted: QColor
    Cursor: QColor
    Underline: QColor
    UnderlineFocused: QColor

colordata = {
    'Light':  {
        ZColorDataKey.Body: lambda: ZPalette.Body,
        ZColorDataKey.BodyFocused: lambda: ZPalette.PanelBody,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.TextBackSectcted: lambda: ZPalette.Secondary,
        ZColorDataKey.Cursor: lambda: ZPalette.Primary,
        ZColorDataKey.Underline: lambda: ZPalette.Underline,
        ZColorDataKey.UnderlineFocused: lambda: ZPalette.Primary
    },
    'Dark': {
        ZColorDataKey.Body: lambda: ZPalette.BodyDarker,
        ZColorDataKey.BodyFocused: lambda: ZPalette.PanelBody,
        ZColorDataKey.Border: lambda: ZPalette.Border,
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.TextBackSectcted: lambda: ZPalette.Primary,
        ZColorDataKey.Cursor: lambda: ZPalette.Primary,
        ZColorDataKey.Underline: lambda: ZPalette.Underline,
        ZColorDataKey.UnderlineFocused: lambda: ZPalette.Primary
    }
}

@colordata_provider(datamap=colordata, classtype=ZNumberEditColorData)

class ZNumberEdit(ZWidget):
    editingFinished = Signal()
    textChanged = Signal(str)

    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    opacityEffectCtrl: ZOpacityEffect
    textColorCtrl: ZAnimatedColor
    textBackColorCtrl: ZAnimatedColor
    cursorColorCtrl: ZAnimatedColor
    underlineColorCtrl: ZAnimatedColor
    underlineWeightCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZNumberEditColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZNumberEdit'},
        'radiusCtrl': {'value': 4.0},
        'underlineWeightCtrl': {'value': 1.3},
    }

    def __init__(self,
                 parent: ZWidget | None = None,
                 text: str = '0',
                 font: QFont = QFont('Microsoft YaHei', 9),
                 integer_digits: int = 10,
                 step: int = 1,
                 allow_decimal: bool = False,
                 decimal_places: int = 2,
                 allow_negative: bool = False,
                 minimumSize: QSize = QSize(200, 30),
                 objectName: str | None = None,
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         minimumSize=minimumSize,
                         font=font
                         )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._text = text
        self._selected_text = ""
        self._allow_decimal = allow_decimal
        self._integer_digits = integer_digits
        self._decimal_places = decimal_places
        self._allow_negative = allow_negative
        self._cursor_pos = len(text)
        self._step = step
        self._selection_start = -1
        self._selection_end = -1
        self._is_selecting = False
        self._focus_select_complete = False
        self._padding = ZPadding(6, 6, 6, 6)
        self._alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        self._undo_stack: list[ZTextSnapshot] = []
        self._redo_stack: list[ZTextSnapshot] = []
        self._max_undo = 20
        self._undo_timer = QTimer(singleShot=True)
        self._undo_timer.timeout.connect(self._commit_undo)
        self._pending_undo = None
        self.cursorColorCtrl.animationAlpha.setDuration(500)
        self.cursorColorCtrl.animationAlpha.finished.connect(self._toggle_cursor)
        self._init_color_data_()


    # region public method
    def text(self) -> str: return self._text

    def setText(self, t: str) -> None:
        self._text = t or ""
        self._cursor_pos = min(self._cursor_pos, len(self._text))
        self.adjustSize()
        self.update()

    def selectedText(self) -> str: return self._selected_text

    def value(self) -> float|int:
        try:
            return float(self._text) if self._allow_decimal else int(self._text)
        except ValueError:
            return 0

    def integerDigits(self) -> int:
        return self._integer_digits

    def setIntegerDigits(self, v: int) -> None:
        if v > 0 and self._integer_digits != v:
            self._integer_digits = v
            self._text = self._validate_text(self._text)
            self.update()

    def decimalPlaces(self) -> int:
        return self._decimal_places

    def setDecimalPlaces(self, v: int) -> None:
        if v >= 0 and self._decimal_places != v:
            self._decimal_places = v
            self._text = self._validate_text(self._text)
            self.update()

    def allowNegative(self) -> bool:
        return self._allow_negative

    def setAllowNegative(self, v: bool) -> None:
        if self._allow_negative != v:
            self._allow_negative = v
            # 如果不允许负数，清除可能存在的负号
            if not v and self._text.startswith('-'):
                self._text = self._text[1:]
                self._cursor_pos = max(0, self._cursor_pos - 1)
            self._text = self._validate_text(self._text)
            self.update()

    def increase(self, auto_repeat=False):
        """按步长增加数值"""
        try:
            value = float(self._text) if self._allow_decimal else int(self._text)
            new_value = value + self._step
            new_text = str(new_value) if self._allow_decimal else str(int(new_value))
            validated_text = self._validate_text(new_text)
            if validated_text != self._text:
                old, oldpos = self._text, self._cursor_pos
                self._text = validated_text
                self._cursor_pos = len(validated_text)
                self._clear_selection()
                if not auto_repeat:
                    self._push_undo_delay(old, self._text, oldpos, self._cursor_pos)
                self.update()
                self.textChanged.emit(self.text())
        except (ValueError, TypeError):
            base_value = 0.0 if self._allow_decimal else 0
            new_value = base_value + self._step
            new_text = str(new_value) if self._allow_decimal else str(int(new_value))
            self._insert_text(new_text, auto_repeat)

    def decrease(self, auto_repeat=False):
        """按步长减少数值"""
        try:
            value = float(self._text) if self._allow_decimal else int(self._text)
            new_value = value - self._step
            new_text = str(new_value) if self._allow_decimal else str(int(new_value))
            validated_text = self._validate_text(new_text)
            if validated_text != self._text:
                old, oldpos = self._text, self._cursor_pos
                self._text = validated_text
                self._cursor_pos = len(validated_text)
                self._clear_selection()
                if not auto_repeat:
                    self._push_undo_delay(old, self._text, oldpos, self._cursor_pos)
                self.update()
                self.textChanged.emit(self.text())
        except (ValueError, TypeError):
            base_value = 0.0 if self._allow_decimal else 0
            new_value = base_value - self._step
            new_text = str(new_value) if self._allow_decimal else str(int(new_value))
            self._insert_text(new_text, auto_repeat)

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        return QSize(max(fm.horizontalAdvance(self._text) + self._padding.horizontal(), self.minimumWidth()),
                     max(fm.height() + self._padding.vertical(), self.minimumHeight()))

    def adjustSize(self):
        self.resize(self.sizeHint())

    # region private method
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border
        self.textColorCtrl.color = data.Text
        self.textBackColorCtrl.color = data.TextBackSectcted
        self.cursorColorCtrl.color = data.Cursor
        self.underlineColorCtrl.color = data.Underline

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        if self.hasFocus():
            self.underlineColorCtrl.setColorTo(data.UnderlineFocused)
            self.bodyColorCtrl.setColorTo(data.BodyFocused)
        else:
            self.underlineColorCtrl.setColorTo(data.Underline)
            self.bodyColorCtrl.setColorTo(data.Body)
        self.cursorColorCtrl.setColorTo(data.Cursor)
        self.borderColorCtrl.setColorTo(data.Border)
        self.textColorCtrl.setColorTo(data.Text)
        self.textBackColorCtrl.setColorTo(data.TextBackSectcted)

    def _validate_text(self, text: str) -> str:
        if not text: return ""

        # 处理负号
        has_negative = text.startswith('-') and self._allow_negative
        if has_negative:
            validated = '-'
            remaining = text[1:]
        else:
            validated = ""
            remaining = text[1:] if text.startswith('-') else text

        # 分离整数和小数部分
        if '.' in remaining:
            integer_part_str, decimal_part_str = remaining.split('.', 1)
            has_decimal = True
        else:
            integer_part_str = remaining
            decimal_part_str = ""
            has_decimal = False

        # 验证整数部分（限制最大位数）
        integer_digits = []
        for c in integer_part_str:
            if c.isdigit():
                # 检查整数部分是否已达到最大位数限制
                if len(integer_digits) < self._integer_digits:
                    # 避免前导零（除非是0本身）
                    if len(integer_digits) == 0 and c == '0' and len(integer_part_str) > 1:
                        continue
                    integer_digits.append(c)

        # 处理空整数部分的情况
        if not integer_digits:
            integer_digits = ['0']

        validated += ''.join(integer_digits)

        # 处理小数部分
        if self._allow_decimal and (has_decimal or self._decimal_places > 0):
            validated += '.'
            decimal_digits = []
            for c in decimal_part_str:
                if c.isdigit() and len(decimal_digits) < self._decimal_places:
                    decimal_digits.append(c)
            # 补零到指定小数位数
            if self._decimal_places > 0:
                decimal_digits += ['0'] * (self._decimal_places - len(decimal_digits))
            validated += ''.join(decimal_digits[:self._decimal_places])

        return validated

    def _filter_valid_chars(self, text: str) -> str:
        """过滤文本中有效的字符"""
        valid_chars = set('0123456789')
        if self._allow_decimal:
            valid_chars.add('.')
        # 只有允许负数时，才允许在开头添加负号
        if self._allow_negative and (not self._text or self._cursor_pos == 0):
            valid_chars.add('-')
        return ''.join([c for c in text if c in valid_chars])

    def _toggle_cursor(self):
        if self.cursorColorCtrl.color.alpha() > 0:
            self.cursorColorCtrl.toTransparent()
        else:
            self.cursorColorCtrl.toOpaque()

    def _should_show_cursor(self) -> bool:
        return (self.hasFocus() and self.cursorColorCtrl.color.alpha() > 0 and not self._selected_text)

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

    # region cut/copy/paste
    def _push_undo(self, old_text: str, new_text: str, old_pos: int, new_pos: int):
        self._undo_stack.append(ZTextSnapshot(old_text, new_text, old_pos, new_pos))
        if len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)

    def _push_undo_delay(self, old_text: str, new_text: str, old_pos: int, new_pos: int):
        if self._undo_timer.isActive():
            # 合并 pending
            if self._pending_undo:
                self._pending_undo[1] = new_text
                self._pending_undo[3] = new_pos
        else:
            self._pending_undo = [old_text, new_text, old_pos, new_pos]
            self._redo_stack.clear()
        self._undo_timer.start(500)

    def _commit_undo(self):
        if self._pending_undo:
            old_text, new_text, old_pos, new_pos = self._pending_undo
            self._push_undo(old_text, new_text, old_pos, new_pos)
            self._pending_undo = None

    def _cut(self):
        if self._is_selection():
            start, end = self._get_selection_range()
            QApplication.clipboard().setText(self._text[start:end])
            old, oldpos = self._text, self._cursor_pos
            self._text = self._text[:start] + self._text[end:]
            self._cursor_pos = start
            self._clear_selection()
            self._push_undo(old, self._text, oldpos, self._cursor_pos)
            self.textChanged.emit(self.text())

    def _copy(self):
        if self._is_selection():
            s, e = self._get_selection_range()
            QApplication.clipboard().setText(self._text[s:e])

    def _paste(self, event: QKeyEvent):
        text = QApplication.clipboard().text()
        if not text: return
        filtered = self._filter_valid_chars(text)
        if not filtered: return

        old, oldpos = self._text, self._cursor_pos
        if self._is_selection():
            s, e = self._get_selection_range()
            temp_text = self._text[:s] + filtered + self._text[e:]
            validated = self._validate_text(temp_text)
            self._text = validated
            self._cursor_pos = min(len(validated), s + len(filtered))
            self._clear_selection()
        else:
            temp_text = self._text[:self._cursor_pos] + filtered + self._text[self._cursor_pos:]
            validated = self._validate_text(temp_text)
            self._text = validated
            self._cursor_pos = min(len(validated), oldpos + len(filtered))

        if not event.isAutoRepeat():
            self._push_undo_delay(old, self._text, oldpos, self._cursor_pos)
        self.update()
        self.textChanged.emit(self.text())

    # region undo/redo
    def _undo(self):
        if self._undo_timer.isActive():
            self._undo_timer.stop()
            self._commit_undo()
        if not self._undo_stack:
            return
        cmd = self._undo_stack.pop()
        self._redo_stack.append(ZTextSnapshot(cmd.old_text, self._text, cmd.old_pos, self._cursor_pos))
        self._text = cmd.old_text
        self._cursor_pos = cmd.old_pos
        self._clear_selection()
        self.update()
        self.textChanged.emit(self.text())

    def _redo(self):
        if self._undo_timer.isActive():
            self._undo_timer.stop()
            self._commit_undo()
        if not self._redo_stack:
            return
        cmd = self._redo_stack.pop()
        self._undo_stack.append(ZTextSnapshot(self._text, cmd.new_text, self._cursor_pos, cmd.new_pos))
        self._text = cmd.new_text
        self._cursor_pos = cmd.new_pos
        self._clear_selection()
        self.update()
        self.textChanged.emit(self.text())

    # region del/backspace/insert
    def _delete_forward(self, auto_repeat=False):
        old, oldpos = self._text, self._cursor_pos
        if self._is_selection():
            s, e = self._get_selection_range()
            self._text = self._text[:s] + self._text[e:]
            self._cursor_pos = s
            self._clear_selection()
        elif self._cursor_pos < len(self._text):
            self._text = self._text[:oldpos] + self._text[oldpos + 1:]
        if not auto_repeat:
            self._push_undo_delay(old, self._text, oldpos, self._cursor_pos)
        self.update()
        self.textChanged.emit(self.text())

    def _insert_text(self, text: str, auto_repeat=False):
        filtered = self._filter_valid_chars(text)
        if not filtered: return

        old, oldpos = self._text, self._cursor_pos
        if self._is_selection():
            s, e = self._get_selection_range()
            temp_text = self._text[:s] + filtered + self._text[e:]
            validated = self._validate_text(temp_text)
            self._text = validated
            self._cursor_pos = min(len(validated), s + len(filtered))
            self._clear_selection()
        else:
            temp_text = self._text[:oldpos] + filtered + self._text[oldpos:]
            validated = self._validate_text(temp_text)
            logging.info("validated: %s", validated)
            self._text = validated
            self._cursor_pos = min(len(validated), oldpos + len(filtered))

        if not auto_repeat:
            self._push_undo_delay(old, self._text, oldpos, self._cursor_pos)
        self.update()
        self.textChanged.emit(self.text())

    def _backspace(self, auto_repeat=False):
        old, oldpos = self._text, self._cursor_pos
        if self._is_selection():
            s, e = self._get_selection_range()
            self._text = self._text[:s] + self._text[e:]
            self._cursor_pos = s
            self._clear_selection()
            if not auto_repeat:
                self._push_undo_delay(old, self._text, oldpos, self._cursor_pos)
            self.update()
            self.textChanged.emit(self.text())
            return
        if self._cursor_pos > 0:
            self._text = self._text[:oldpos - 1] + self._text[oldpos:]
            self._cursor_pos -= 1
            if not auto_repeat:
                self._push_undo_delay(old, self._text, oldpos, self._cursor_pos)
            self.update()
            self.textChanged.emit(self.text())


    def _text_rect(self) -> QRectF:
        r = QRectF(self.rect())
        return QRectF(r.left() + self._padding.left,
                      r.top() + self._padding.top,
                      r.width() - (self._padding.horizontal()),
                      r.height() - (self._padding.vertical()))

    def _get_layout_y(self, text_rect: QRectF, fm: QFontMetrics) -> float:
        line_h = fm.height()
        if self._alignment & Qt.AlignmentFlag.AlignVCenter:
            return text_rect.top() + (text_rect.height() - line_h) / 2
        if self._alignment & Qt.AlignmentFlag.AlignBottom:
            return text_rect.bottom() - line_h
        return text_rect.top()

    def _draw_selection_background(self, painter: QPainter, text_rect: QRectF, fm: QFontMetrics):
        s, e = self._get_selection_range()
        display = self._text
        if s >= e:
            return
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.textBackColorCtrl.color)
        line_y = self._get_layout_y(text_rect, fm)
        # selection relative indices within display
        sel_start = max(0, s)
        sel_end = min(len(display), e)
        x1 = text_rect.left() + fm.horizontalAdvance(display[:sel_start])
        x2 = text_rect.left() + fm.horizontalAdvance(display[:sel_end])
        sel_rect = QRectF(x1, line_y + 1, max(0.0, x2 - x1), max(0.0, fm.height() - 2))
        painter.drawRoundedRect(sel_rect, 2, 2)
        painter.restore()

    def _get_char_position_at_point(self, point: QPoint) -> int:
        fm = QFontMetrics(self.font())
        text_rect = self._text_rect()
        # y 检查
        line_y = self._get_layout_y(text_rect, fm)
        if point.y() < line_y or point.y() > line_y + fm.height():
            return self._cursor_pos
        # 将点击映射为 display 中的 x
        click_x = point.x() - text_rect.left()
        acc = 0
        for i, ch in enumerate(self._text):
            w = fm.horizontalAdvance(ch)
            if click_x <= acc + w / 2:
                return min(i, len(self._text))
            acc += w
        return len(self._text)

    # region paintEvent
    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value
        clip = QPainterPath()
        clip.addRoundedRect(rect, radius, radius)
        painter.setClipPath(clip)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(rect, self.bodyColorCtrl.color)

        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        if self.opacityEffectCtrl.color.alpha() > 0:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.opacityEffectCtrl.color)
            painter.drawRoundedRect(rect, radius, radius)

        underline_h = self.underlineWeightCtrl.value
        painter.fillRect(QRectF(rect.left(), rect.bottom() - underline_h, rect.width(), underline_h),
                            self.underlineColorCtrl.color)

        # 文本区域
        painter.setFont(self.font())
        fm = QFontMetrics(self.font())
        text_rect = self._text_rect()
        display = self._text

        self._update_selected_text()

         # 选区背景
        if self._is_selection() and self._text:
            self._draw_selection_background(painter, text_rect, fm)

        # 绘制文本
        painter.setPen(self.textColorCtrl.color)
        x = text_rect.left()
        y = self._get_layout_y(text_rect, fm) + fm.ascent()
        painter.drawText(QPointF(x, y), display)

        # 绘制光标（若应显示）
        if self._should_show_cursor():
            fm_draw = QFontMetrics(self.font())
            layout_y = self._get_layout_y(text_rect, fm_draw)
            # 计算 cursor 在 display 文本中的索引
            display_text = display
            cursor_display_idx = self._cursor_pos
            cursor_x = text_rect.left() + fm_draw.horizontalAdvance(display_text[:cursor_display_idx])
            cursor_top = layout_y
            cursor_bottom = cursor_top + fm_draw.height()
            painter.setPen(self.cursorColorCtrl.color)
            painter.drawLine(QPointF(cursor_x, cursor_top), QPointF(cursor_x, cursor_bottom))

        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
        event.accept()

    # region keyPressEvent
    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        self.cursorColorCtrl.toOpaque()
        # 通用 Ctrl 快捷
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C and self._is_selection():
                self._copy(); return
            if event.key() == Qt.Key.Key_A:
                self._selection_start = 0
                self._selection_end = len(self._text)
                self.update()
                return
            if event.key() == Qt.Key.Key_V:
                self._paste(event)
                return
            if event.key() == Qt.Key.Key_Z:
                self._undo()
                return
            if event.key() == Qt.Key.Key_Y:
                self._redo()
                return
            if event.key() == Qt.Key.Key_X:
                self._cut()
                return
            event.ignore()
            return
        if event.key() == Qt.Key.Key_Left:
            if self._is_selection():
                self._clear_selection()
            elif self._cursor_pos > 0:
                self._cursor_pos -= 1
            self.update(); return
        if event.key() == Qt.Key.Key_Right:
            if self._is_selection():
                self._clear_selection()
            elif self._cursor_pos < len(self._text):
                self._cursor_pos += 1
            self.update(); return
        if event.key() == Qt.Key.Key_Backspace:
            self._backspace(event.isAutoRepeat()); return
        if event.key() == Qt.Key.Key_Delete:
            self._delete_forward(event.isAutoRepeat()); return
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.editingFinished.emit(); return
        if event.text():
            self._insert_text(event.text(), event.isAutoRepeat()); return

    # region mouseEvent
    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            if self._focus_select_complete:
                self._focus_select_complete = False
                return
            pos = self._get_char_position_at_point(event.position())
            self._cursor_pos = pos
            self.cursorColorCtrl.toOpaque()
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if self._selection_start == -1:
                    self._selection_start = 0
                self._selection_end = pos
            else:
                self._selection_start = pos
                self._selection_end = pos
                self._is_selecting = True
            self.update()


    def mouseMoveEvent(self, event: QMouseEvent):
        if self._is_selecting:
            new_pos = self._get_char_position_at_point(event.position())
            self._selection_end = new_pos
            self._cursor_pos = new_pos
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_selecting = False

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.cursorColorCtrl.toOpaque()
        self._selection_start = 0
        self._selection_end = len(self._text)
        self._focus_select_complete = True
        self.bodyColorCtrl.setColorTo(self.colorDataCtrl.data.BodyFocused)
        self.underlineColorCtrl.setColorTo(self.colorDataCtrl.data.UnderlineFocused)
        self.underlineWeightCtrl.setValueTo(1.8)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.cursorColorCtrl.transparent()
        self.cursorColorCtrl.stopAnimation()
        self.bodyColorCtrl.setColorTo(self.colorDataCtrl.data.Body)
        self.underlineColorCtrl.setColorTo(self.colorDataCtrl.data.Underline)
        self.underlineWeightCtrl.setValueTo(1.4)
        self._clear_selection()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.opacityEffectCtrl.setAlphaFTo(0.04)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.opacityEffectCtrl.toTransparent()

    def wheelEvent(self, event: QWheelEvent):
        super().wheelEvent(event)
        if self.hasFocus():
            delta = event.angleDelta().y()
            if delta > 0:
                self.increase()
            else:
                self.decrease()
        event.accept()

# import sys
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = QWidget()
#     layout = QVBoxLayout()
#     window.setLayout(layout)
#     edit = ZNumberEdit(window)
#     edit2 = ZNumberEdit(window,allow_decimal=False)
#     layout.addWidget(edit)
#     layout.addWidget(edit2)
#     # edit.valueChanged.connect(print)
#     # edit.editingFinished.connect(lambda: print("edit finished"))
#     window.show()
#     sys.exit(app.exec())