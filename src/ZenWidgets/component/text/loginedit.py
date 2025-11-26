import logging
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout
from PySide6.QtCore import Signal,QSize,QTimer,QPoint,QPointF,QRectF,Qt
from PySide6.QtGui import QFontMetrics,QFont,QMouseEvent,QPainterPath,QPainter,QKeyEvent,QPen
from ZenWidgets.component.base import (
    ZOpacityEffect,
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController,
    ZWidget
)
from ZenWidgets.core import ZDebug,ZPadding,ZTextSnapshot
from ZenWidgets.gui import ZLoginEditColorData

class ZLoginEdit(ZWidget):
    editingFinished = Signal()
    valueChanged = Signal(str)

    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    opacityEffectCtrl: ZOpacityEffect
    textColorCtrl: ZAnimatedColor
    textBackColorCtrl: ZAnimatedColor
    cursorColorCtrl: ZAnimatedColor
    underlineColorCtrl: ZAnimatedColor
    underlineWeightCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZLoginEditColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZLoginEdit'},
        'radiusCtrl': {'value': 4.0},
        'underlineWeightCtrl': {'value': 1.3},
    }
    def __init__(self,
                 parent: QWidget | ZWidget | None = None,
                 text: str = '',
                 font: QFont = QFont('Microsoft YaHei', 9),
                 digits: int = 0,
                 is_masked = False,
                 allow_characters = True,
                 minimumSize: QSize = QSize(200, 30),
                 objectName: str | None = None,
                 ):
        super().__init__(parent=parent,
                         objectName=objectName,
                         minimumSize=minimumSize,
                         font=font
                         )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._text = ''
        self._selected_text = ""
        self._cursor_pos = len(text)
        self._selection_start = -1
        self._selection_end = -1
        self._is_selecting = False
        self._digits = digits
        self._is_masked = is_masked
        self._allow_characters = allow_characters
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

    def sizeHint(self) -> QSize:
        fm = QFontMetrics(self.font())
        return QSize(max(fm.horizontalAdvance(self._text) + self._padding.horizontal(), self.minimumWidth()),
                     max(fm.height() + self._padding.vertical(), self.minimumHeight()))

    def adjustSize(self):
        self.resize(self.sizeHint())

    # region private method
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text
        self.textBackColorCtrl.color = data.TextBackSectcted
        self.cursorColorCtrl.color = data.Cursor
        self.underlineColorCtrl.color = data.Underline
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border

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
        if text is None:
            return ""
        # 保留所有允许字符（类型过滤在 _filter_valid_chars 中已做），这里只负责长度限制
        if self._digits is None or self._digits <= 0:
            return text
        # 截断到最大位数
        return text[: self._digits]

    def _filter_valid_chars(self, text: str) -> str:
        """过滤文本中有效的字符"""
        if not text:
            return ""
        out_chars = []
        for ch in text:
            # 跳过控制字符
            if ch in ("\n", "\r", "\t"):
                continue
            # 当不允许字符输入时，只保留数字
            if not self._allow_characters:
                if ch.isdigit():
                    out_chars.append(ch)
            else:
                # 允许所有可见字符（排除非打印字符）
                # 简单判断：使用 isprintable()
                if ch.isprintable():
                    out_chars.append(ch)
        return "".join(out_chars)

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
            self.valueChanged.emit(self.text())

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
        self.valueChanged.emit(self.text())

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
        self.valueChanged.emit(self.text())

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
        self.valueChanged.emit(self.text())

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
        self.valueChanged.emit(self.text())

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
        self.valueChanged.emit(self.text())

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
            self.valueChanged.emit(self.text())
            return
        if self._cursor_pos > 0:
            self._text = self._text[:oldpos - 1] + self._text[oldpos:]
            self._cursor_pos -= 1
            if not auto_repeat:
                self._push_undo_delay(old, self._text, oldpos, self._cursor_pos)
            self.update()
            self.valueChanged.emit(self.text())


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
        display = "•" * len(self._text) if self._is_masked else self._text
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
        # 使用显示文本进行 hit-test（遮罩时使用掩码字符）
        display = "•" * len(self._text) if self._is_masked else self._text
        click_x = point.x() - text_rect.left()
        acc = 0.0
        for i, ch in enumerate(display):
            w = fm.horizontalAdvance(ch)
            if click_x <= acc + w / 2:
                # 返回逻辑索引（与真实文本长度一致）
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
            painter.setPen(Qt.PenStyle.NoPen)
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

        if self._is_masked:
            display = "•" * len(self._text)
        else:
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
            self.update()
            return
        if event.key() == Qt.Key.Key_Right:
            if self._is_selection():
                self._clear_selection()
            elif self._cursor_pos < len(self._text):
                self._cursor_pos += 1
            self.update()
            return
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

import sys
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)
    edit = ZLoginEdit(window,allow_characters=False)
    edit2 = ZLoginEdit(window,is_masked=True)
    layout.addWidget(edit)
    layout.addWidget(edit2)
    # edit.valueChanged.connect(print)
    # edit.editingFinished.connect(lambda: print("edit finished"))
    window.show()
    sys.exit(app.exec())