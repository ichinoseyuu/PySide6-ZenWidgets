from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout
from PySide6.QtCore import Signal,QSize,Qt
from PySide6.QtGui import QFont,QColor
from ZenWidgets.component.input.button import ZButton
from ZenWidgets.component.base import (
    ZColorController,
    ZWidget,
)
from ZenWidgets.component.text.lineedit import ZLineEdit
from ZenWidgets.core import ZGlobal
from ZenWidgets.gui import ZButtonStyle
from ZenWidgets.gui import (
    ZColorData,
    ZColorDataKey,
    ZPalette,
    colordata_provider
)
from .inputfilter import TextFilter, ZTextFilter

class ZPasswordEditColorData(ZColorData):
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

@colordata_provider(name='ZPasswordEdit', datamap=colordata, classtype=ZPasswordEditColorData)
class ZPasswordEdit(ZLineEdit):
    valueChanged = Signal(str)

    colorDataCtrl: ZColorController[ZPasswordEditColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl': {'key': 'ZPasswordEdit'},
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 text: str = '',
                 font: QFont = QFont('Microsoft YaHei', 9),
                 is_masked = True,
                 minimumSize: QSize = QSize(200, 30),
                 objectName: str | None = None,
                 input_filter: TextFilter | None = None,
                 ):
        password_filter = ZTextFilter.printableOnly()
        if input_filter is not None:
            password_filter = ZTextFilter.compose(password_filter, input_filter)
        super().__init__(parent=parent,
                         text="",
                         objectName=objectName,
                         minimumSize=minimumSize,
                         font=font,
                         input_filter=password_filter,
                         )
        self._is_masked = is_masked
        self.setText(text)
        self._cursor_pos = len(self._text)
        self._visibility_button = ZButton(
            self,
            icon_size=QSize(16, 16),
            style=ZButtonStyle.Flat,
            toolTip='显示密码',
        )
        self._visibility_button.setFixedSize(QSize(26, 26))
        self._visibility_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._visibility_button.clicked.connect(self._toggle_password_visibility_)
        self._set_action_buttons_(self._visibility_button)
        self._update_visibility_button_()

    def _toggle_password_visibility_(self) -> None:
        self._is_masked = not self._is_masked
        self._update_visibility_button_()
        self.update()

    def _update_visibility_button_(self) -> None:
        icon_name = 'ic_fluent_eye_regular' if self._is_masked else 'ic_fluent_eye_off_regular'
        tooltip = '显示密码' if self._is_masked else '隐藏密码'
        self._visibility_button.setIcon(ZGlobal.iconPack.toIcon(icon_name, QSize(16, 16)))
        self._visibility_button.setToolTip(tooltip)
        self._visibility_button.setProperty('_zen_action_visible', True)
        self._visibility_button.show()
        self._update_action_button_padding_()
        self._layout_action_buttons_()

    def _format_text_for_display(self, text: str) -> str:
        return "•" * len(text) if self._is_masked else text

    def _emit_text_changed(self) -> None:
        super()._emit_text_changed()
        self.valueChanged.emit(self.text())
import sys
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)
    edit = ZPasswordEdit(window)
    edit2 = ZPasswordEdit(window, is_masked=False)
    layout.addWidget(edit)
    layout.addWidget(edit2)
    # edit.valueChanged.connect(print)
    # edit.editingFinished.connect(lambda: print("edit finished"))
    window.show()
    sys.exit(app.exec())