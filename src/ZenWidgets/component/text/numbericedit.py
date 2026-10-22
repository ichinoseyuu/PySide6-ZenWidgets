from PySide6.QtCore import Signal,QSize,Qt
from PySide6.QtGui import QFont,QWheelEvent,QColor
from ZenWidgets.component.base import (
    ZColorController,
    ZWidget,
)
from ZenWidgets.component.text.lineedit import ZLineEdit
from ZenWidgets.component.input.repeatbutton import ZRepeatButton
from ZenWidgets.core import ZGlobal

from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    ZButtonStyle,
    colordata_provider
)
from .inputfilter import TextFilter

class ZNumericEditColorData(ZColorData):
    Body: QColor
    BodyFocused: QColor
    Border: QColor
    Text: QColor
    PlaceHolder: QColor
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
        ZColorDataKey.PlaceHolder: lambda: ZPalette.TextMuted,
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
        ZColorDataKey.PlaceHolder: lambda: ZPalette.TextMuted,
        ZColorDataKey.TextBackSectcted: lambda: ZPalette.Primary,
        ZColorDataKey.Cursor: lambda: ZPalette.Primary,
        ZColorDataKey.Underline: lambda: ZPalette.Underline,
        ZColorDataKey.UnderlineFocused: lambda: ZPalette.Primary
    }
}

@colordata_provider(name='ZNumericEdit', datamap=colordata, classtype=ZNumericEditColorData)

class ZNumericEdit(ZLineEdit):
    colorDataCtrl: ZColorController[ZNumericEditColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl': {'key': 'ZNumericEdit'},
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
                 input_filter: TextFilter | None = None,
                 ):
        super().__init__(parent=parent,
             text="",
                         objectName=objectName,
                         minimumSize=minimumSize,
                         font=font,
                         input_filter=input_filter,
                         )
        self._allow_decimal = allow_decimal
        self._integer_digits = integer_digits
        self._decimal_places = decimal_places
        self._allow_negative = allow_negative
        self._step = step
        self._select_all_on_focus = True
        self.setText(text)
        self._cursor_pos = len(self._text)
        self._pressed_step_button = None
        self._repeat_happened = False
        self._repeat_start_state = None
        self._skip_release_click = False
        self._decrease_button = ZRepeatButton(
            self,
            icon=ZGlobal.iconPack.toIcon('ic_fluent_chevron_down_filled', QSize(16, 16)),
            icon_size=QSize(16, 16),
            style=ZButtonStyle.Flat,
            interval=100,
            delay=400,
            toolTip='减少数值',
            toolTipDelay=500
        )
        self._increase_button = ZRepeatButton(
            self,
            icon=ZGlobal.iconPack.toIcon('ic_fluent_chevron_up_filled', QSize(16, 16)),
            icon_size=QSize(16, 16),
            style=ZButtonStyle.Flat,
            interval=100,
            delay=400,
            toolTip='增加数值',
            toolTipDelay=500
        )
        self._decrease_button.setFixedSize(QSize(26, 26))
        self._increase_button.setFixedSize(QSize(26, 26))
        for button in (self._decrease_button, self._increase_button):
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.pressed.connect(self._begin_step_press_)
            button.clicked.connect(self._handle_step_click_)
            button.released.connect(self._finish_step_press_)
        self._set_action_buttons_(self._decrease_button, self._increase_button)

    def _begin_step_press_(self) -> None:
        self._pressed_step_button = self.sender()
        self._repeat_happened = False
        self._repeat_start_state = (self._text, self._cursor_pos)
        self._skip_release_click = False

    def _handle_step_click_(self) -> None:
        button = self.sender()
        if button is self._pressed_step_button and button.isPressed():
            self._repeat_happened = True
            self._apply_step_(button, auto_repeat=True)
            return
        if self._skip_release_click:
            self._skip_release_click = False
            return
        self._apply_step_(button)

    def _apply_step_(self, button: ZRepeatButton, auto_repeat: bool = False) -> None:
        if button is self._increase_button:
            self.increase(auto_repeat=auto_repeat)
        else:
            self.decrease(auto_repeat=auto_repeat)

    def _finish_step_press_(self) -> None:
        button = self.sender()
        if button is not self._pressed_step_button:
            return
        if self._repeat_happened and self._repeat_start_state:
            if self._undo_timer.isActive():
                self._undo_timer.stop()
                if self._pending_undo and self._pending_undo[0] == self._pending_undo[1]:
                    self._pending_undo = None
                else:
                    self._commit_undo()
            if self._text != self._repeat_start_state[0]:
                self._redo_stack.clear()
                self._push_undo(
                    self._repeat_start_state[0], self._text,
                    self._repeat_start_state[1], self._cursor_pos,
                )
            self._skip_release_click = True
        self._pressed_step_button = None
        self._repeat_happened = False
        self._repeat_start_state = None

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
            self.setText(self._text)

    def decimalPlaces(self) -> int:
        return self._decimal_places

    def setDecimalPlaces(self, v: int) -> None:
        if v >= 0 and self._decimal_places != v:
            self._decimal_places = v
            self.setText(self._text)

    def allowNegative(self) -> bool:
        return self._allow_negative

    def setAllowNegative(self, v: bool) -> None:
        if self._allow_negative != v:
            self._allow_negative = v
            # 如果不允许负数，清除可能存在的负号
            text = self._text
            if not v and text.startswith('-'):
                text = text[1:]
                self._cursor_pos = max(0, self._cursor_pos - 1)
            self.setText(text)

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

    def _filter_valid_chars(self,
                            text: str,
                            start: int | None = None,
                            end: int | None = None,
                            ) -> str:
        """过滤文本中有效的字符"""
        if start is None or end is None:
            if self._is_selection():
                start, end = self._get_selection_range()
            else:
                start = end = self._cursor_pos
        text = super()._filter_valid_chars(text, start, end)
        valid_chars = set('0123456789')
        if self._allow_decimal:
            valid_chars.add('.')
        allow_negative = self._allow_negative and not self._text[:start]
        filtered = []
        for index, char in enumerate(text):
            if char in valid_chars or (char == '-' and allow_negative and index == 0):
                filtered.append(char)
        return ''.join(filtered)

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