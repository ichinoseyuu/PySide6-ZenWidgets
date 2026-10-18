from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout
from PySide6.QtCore import Signal,QSize
from PySide6.QtGui import QFont,QColor
from ZenWidgets.component.base import (
    ZColorController,
    ZWidget,
)
from ZenWidgets.component.text.lineedit import ZLineEdit
from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)

class ZLoginEditColorData(ZColorData):
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

@colordata_provider(name='ZLoginEdit', datamap=colordata, classtype=ZLoginEditColorData)
class ZPasswordEdit(ZLineEdit):
    valueChanged = Signal(str)

    colorDataCtrl: ZColorController[ZLoginEditColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl': {'key': 'ZLoginEdit'},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 text: str = '',
                 font: QFont = QFont('Microsoft YaHei', 9),
                 digits: int = 0,
                 is_masked = True,
                 allow_characters = True,
                 minimumSize: QSize = QSize(200, 30),
                 objectName: str | None = None,
                 ):
        super().__init__(parent=parent,
                         text=text,
                         objectName=objectName,
                         minimumSize=minimumSize,
                         font=font
                         )
        self._digits = digits
        self._is_masked = is_masked
        self._allow_characters = allow_characters
        self._cursor_pos = len(self._text)

    # region input policy
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

    def _format_text_for_display(self, text: str) -> str:
        return "•" * len(text) if self._is_masked else text

    def _emit_text_changed(self) -> None:
        self.valueChanged.emit(self.text())

class ZLoginEdit(ZPasswordEdit):
    """兼容旧名称，默认不遮罩文本。"""

    def __init__(self,
                 parent: ZLineEdit | None = None,
                 text: str = '',
                 font: QFont = QFont('Microsoft YaHei', 9),
                 digits: int = 0,
                 is_masked: bool = False,
                 allow_characters: bool = True,
                 minimumSize: QSize = QSize(200, 30),
                 objectName: str | None = None,
                 ):
        super().__init__(parent=parent,
                         text=text,
                         font=font,
                         digits=digits,
                         is_masked=is_masked,
                         allow_characters=allow_characters,
                         minimumSize=minimumSize,
                         objectName=objectName)

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