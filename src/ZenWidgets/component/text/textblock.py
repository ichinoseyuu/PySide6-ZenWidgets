from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt,QSize,QRectF,QPoint
from PySide6.QtGui import QPainter,QFont,QFontMetrics,QPen,QTextLayout,QTextOption,QColor
from ZenWidgets.component.base import (
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController,
    ZWidget
)
from ZenWidgets.core import ZDebug,ZPadding,ZWrapMode
from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

class ZTextBlockColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    TextBackSectcted: QColor

colordata = {
    'Light':  {
        ZColorDataKey.Body: ZPalette.Transparent_000,
        ZColorDataKey.Border: ZPalette.Transparent_000,
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.TextBackSectcted: lambda: ZPalette.Primary
    },
    'Dark': {
        ZColorDataKey.Body: ZPalette.Transparent_000,
        ZColorDataKey.Border: ZPalette.Transparent_000,
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.TextBackSectcted: lambda: ZPalette.Primary
    }
}

@colordata_provider(datamap=colordata, classtype=ZTextBlockColorData)
class ZTextBlock(ZWidget):
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    textColorCtrl: ZAnimatedColor
    textBackColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[ZTextBlockColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'ZTextBlock'},
        'radiusCtrl': {'value': 4.0}
    }

    def __init__(self,
                 parent: QWidget | None = None,
                 text: str = "",
                 font: QFont = QFont('Microsoft YaHei', 9),
                 wrap_mode: ZWrapMode = ZWrapMode.WordWrap,
                 selectable: bool = False,
                 height_for_width: bool = True,
                 objectName: str | None = None,
                 ):
        super().__init__(parent=parent,
                         height_for_width=height_for_width,
                         objectName=objectName,
                         font=font
                         )
        if selectable: self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self._text = text
        self._selected_text = ""
        self._padding = ZPadding(4, 4, 4, 4)
        self._wrap_mode = wrap_mode
        self._alignment = Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter
        self._selectable = selectable
        self._selection_start = -1
        self._selection_end = -1
        self._is_selecting = False
        self._select_start_pos: QPoint | None = None
        self._init_color_data_()
        self.setMinimumSize(self._padding.horizontal(), 24)

    # region public
    def selectedText(self) -> str: return self._selected_text

    def text(self) -> str: return self._text

    def setText(self, text: str) -> None:
        self._text = text
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

    def wrapMode(self) ->ZWrapMode: return self._wrap_mode

    def setWrapMode(self, mode: ZWrapMode) -> None:
        self._wrap_mode = mode
        self.adjustSize()
        self.update()

    def padding(self) -> ZPadding: return self._padding

    def setPadding(self, p: ZPadding) -> None:
        self._padding = p
        self.adjustSize()
        self.update()

    def alignment(self) -> Qt.AlignmentFlag: return self._alignment

    def setAlignment(self, a: Qt.AlignmentFlag) -> None:
        self._alignment = a
        self.update()

    def sizeHint(self):
        m = self._padding
        if not self._text: return QSize(m.horizontal(), self.minimumHeight())
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self._text) + m.horizontal() + 1
        if self._wrap_mode == ZWrapMode.NoWrap:
            height = max(fm.height() + m.vertical(), self.minimumHeight())
            return QSize(text_width, height)
        width = self.width()
        height = self._caculate_text_layout(width)
        return QSize(width, height)

    def adjustSize(self): self.resize(self.sizeHint())

    def heightForWidth(self, width: int) -> int: return self._caculate_text_layout(width)

    def _caculate_text_layout(self, width: int) -> int:
        m = self._padding
        fm = QFontMetrics(self.font())
        available_width = width - m.horizontal()
        if self._wrap_mode == ZWrapMode.NoWrap:
            return max(fm.height() + m.vertical(), self.minimumHeight())
        layout = QTextLayout(self._text, self.font())
        option = QTextOption()
        if self._wrap_mode == ZWrapMode.WordWrap:
            option.setWrapMode(QTextOption.WrapMode.WordWrap)
        else:
            option.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
        layout.setTextOption(option)

        layout.beginLayout()
        total_height = 0
        while True:
            line = layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(available_width)
            total_height += line.height()
        layout.endLayout()
        return max(total_height + m.vertical(), self.minimumHeight())

    # region private
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text
        self.bodyColorCtrl.color = data.Body
        self.borderColorCtrl.color = data.Border
        self.textBackColorCtrl.color = data.TextBackSectcted

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.borderColorCtrl.setColorTo(data.Border)
        self.textColorCtrl.setColorTo(data.Text)
        self.textBackColorCtrl.setColorTo(data.TextBackSectcted)


    def _is_selection(self) -> bool:
        return (self._selection_start != -1 and self._selection_end != -1
                and self._selection_start != self._selection_end)

    def _get_selection_range(self) -> tuple:
        return (min(self._selection_start, self._selection_end),
                max(self._selection_start, self._selection_end))

    def _get_text_flag(self) -> Qt.TextFlag:
        if self._wrap_mode == ZWrapMode.NoWrap:
            return Qt.TextFlag.TextSingleLine | self._alignment
        elif self._wrap_mode == ZWrapMode.WordWrap:
            return Qt.TextFlag.TextWordWrap | self._alignment
        else:
            return Qt.TextFlag.TextWrapAnywhere | self._alignment

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

    def _get_text_layout(self, text_rect: QRectF, fm: QFontMetrics):
        """获取文本的行布局信息，返回每行的文本内容、在原文本中的位置和精确的 Y 坐标"""
        if self._wrap_mode == ZWrapMode.NoWrap:
            line_height = fm.height()
            if self._alignment & Qt.AlignmentFlag.AlignVCenter:
                y_pos = text_rect.top() + (text_rect.height() - line_height) / 2
            elif self._alignment & Qt.AlignmentFlag.AlignBottom:
                y_pos = text_rect.bottom() - line_height
            else:
                y_pos = text_rect.top()
            return [(self._text, 0, y_pos)]

        layout = QTextLayout(self._text, self.font())
        option = QTextOption()

        if self._wrap_mode == ZWrapMode.WordWrap:
            option.setWrapMode(QTextOption.WrapMode.WordWrap)
        elif self._wrap_mode == ZWrapMode.WrapAnywhere:
            option.setWrapMode(QTextOption.WrapMode.WrapAnywhere)

        horizontal_alignment = self._alignment & (
            Qt.AlignmentFlag.AlignLeft |
            Qt.AlignmentFlag.AlignRight |
            Qt.AlignmentFlag.AlignHCenter
            )
        option.setAlignment(horizontal_alignment)
        layout.setTextOption(option)

        layout.beginLayout()
        lines_info = []

        temp_lines = []
        while True:
            line = layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(text_rect.width())
            temp_lines.append(line)

        layout.endLayout()

        total_height = sum(line.height() for line in temp_lines)

        if self._alignment & Qt.AlignmentFlag.AlignVCenter:
            start_y = text_rect.top() + (text_rect.height() - total_height) / 2
        elif self._alignment & Qt.AlignmentFlag.AlignBottom:
            start_y = text_rect.bottom() - total_height
        else:
            start_y = text_rect.top()

        current_y = start_y
        for line in temp_lines:
            line_text = self._text[line.textStart():line.textStart() + line.textLength()]
            lines_info.append((line_text, line.textStart(), current_y))
            current_y += line.height()

        return lines_info


    def _get_char_position_at_point(self, point):
        """根据坐标点获取字符位置"""
        if not self._text:
            return 0

        m = self._padding
        text_rect = self.rect().adjusted(m.left, m.top, -m.right, -m.bottom)
        fm = QFontMetrics(self.font())

        lines_info = self._get_text_layout(text_rect, fm)
        click_y = point.y()

        line_index = -1
        for i, (line_text, line_start_pos, line_y) in enumerate(lines_info):
            line_height = fm.height()
            if click_y >= line_y and click_y <= line_y + line_height:
                line_index = i
                break

        if line_index == -1:
            if click_y < lines_info[0][2]:
                line_index = 0
            else:
                line_index = len(lines_info) - 1

        line_text, line_start_pos, _ = lines_info[line_index]
        click_x = point.x() - text_rect.left()

        char_pos_in_line = 0
        accumulated_width = 0
        for i, char in enumerate(line_text):
            char_width = fm.horizontalAdvance(char)
            if click_x <= accumulated_width + char_width / 2:
                char_pos_in_line = i
                break
            accumulated_width += char_width
            char_pos_in_line = i + 1

        return min(line_start_pos + char_pos_in_line, len(self._text))


    def _draw_selection_background(self, painter: QPainter, text_rect: QRectF, start: int, end: int, fm: QFontMetrics):
        """绘制选中区域背景（统一处理单行和多行）"""
        if start >= end: return

        lines_info = self._get_text_layout(text_rect, fm)
        line_height = fm.height() + 2

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.textBackColorCtrl.color)

        for line_text, line_start_pos, line_y in lines_info:
            line_end_pos = line_start_pos + len(line_text)

            if start >= line_end_pos or end <= line_start_pos:
                continue

            line_sel_start = max(0, start - line_start_pos)
            line_sel_end = min(len(line_text), end - line_start_pos)

            if line_sel_start < line_sel_end:
                x1 = text_rect.left()
                if line_sel_start > 0:
                    x1 += fm.horizontalAdvance(line_text[:line_sel_start])

                x2 = x1 + fm.horizontalAdvance(line_text[line_sel_start:line_sel_end])

                selection_rect = QRectF(x1, line_y + 1, x2 - x1, line_height - 2)
                painter.drawRoundedRect(selection_rect, 2, 2)


    # region paintEvent
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.TextAntialiasing|
            QPainter.RenderHint.Antialiasing
            )
        rect = QRectF(self.rect())
        radius = self.radiusCtrl.value

        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        m = self._padding
        text_rect = rect.adjusted(m.left, m.top, -m.right, -m.bottom)

        self._update_selected_text()

        if self._selectable and self._is_selection() and self._text:
            start, end = self._get_selection_range()
            if start < end:
                fm = QFontMetrics(self.font())
                self._draw_selection_background(painter, text_rect, start, end, fm)

        painter.setFont(self.font())
        painter.setPen(self.textColorCtrl.color)
        text_flags = self._get_text_flag()
        painter.drawText(text_rect, text_flags, self._text)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, rect)
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
                self._select_start_pos = event.pos()
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.hasHeightForWidth():
            new_height = self.heightForWidth(event.size().width())
            if new_height != event.size().height():
                self.resize(event.size().width(), new_height)