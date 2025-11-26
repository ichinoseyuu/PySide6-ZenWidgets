import copy
from typing import Dict,Generic
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal,Slot
from PySide6.QtGui import QColor
from ZenWidgets.core import ZGlobal
from ZenWidgets.gui import ColorDataT,ZColorDataKey

__all__ = ['ZColorController']

class ZColorController(QObject, Generic[ColorDataT]):
    '''颜色数据管理器
    - 决定控件的当前颜色
    - 存储自定义颜色数据
    '''
    styleChanged = Signal()
    def __init__(self, parent: QWidget, key: str=''):
        super().__init__(parent)
        self._custom: bool = False
        self._key: str = key
        self._data: ColorDataT = None
        self._custom_data: Dict[str, ColorDataT] = {'Light': None, 'Dark': None}
        if key: self._data = ZGlobal.styleDataManager.getStyleData(key)
        ZGlobal.themeManager.themeChanged.connect(self._theme_change_handler_)

    @property
    def data(self) -> ColorDataT: return self._data

    @Slot(str)
    def _theme_change_handler_(self, theme:str) -> None:
        '''
        接收主题改变信号,更新样式数据的槽函数
        '''
        if self._custom:
            self._data = self._custom_data[theme]
        else:
            self._data = ZGlobal.styleDataManager.getStyleData(self._key)
        self.styleChanged.emit()

    def setKey(self, key: str, /, update: bool = False) -> None:
        '''
        设置样式数据键,用于获取指定样式数据

        :param key: 样式数据键
        :param update: 是否立即更新样式数据
        '''
        self._key = key
        self._data = ZGlobal.styleDataManager.getStyleData(key)
        if update: self.styleChanged.emit()


    def setCustomDataComplete(self, theme: str, data: ColorDataT, /, update: bool = False) -> None:
        '''
        完全自定义样式数据

        :param theme: 主题
        :param data: 样式数据
        '''
        if theme not in self._custom_data:
            raise ValueError(f"不支持的主题: {theme}，必须是 'Light' 或 'Dark'")
        self._custom_data[theme] = data
        self._custom = True
        if update and theme == ZGlobal.themeManager.getThemeName():
            self._data = data
            self.styleChanged.emit()

    def setCustomData(self, theme: str, data_key: ZColorDataKey, value: QColor, /, update: bool = False) -> None:
        '''
        自定义样式数据中的特定字段

        :param theme: 主题
        :param data_key: 要修改的样式数据字段键
        :param value: 要设置的新值
        '''
        if theme not in self._custom_data:
            raise ValueError(f"不支持的主题: {theme}，必须是 'Light' 或 'Dark'")
        # 获取基础数据（优先用已有自定义数据，否则用默认数据）
        base_data = self._custom_data[theme] if self._custom_data[theme] is not None else ZGlobal.styleDataManager.getStyleDataByTheme(self._key, theme)
        new_data = copy.deepcopy(base_data)
        if not hasattr(new_data, data_key.value):
            raise AttributeError(f"StyleDataT 没有字段: {data_key}")
        setattr(new_data, data_key.value, value)
        self._custom_data[theme] = new_data
        self._custom = True
        if update and theme == ZGlobal.themeManager.getThemeName():
            self._data = new_data
            self.styleChanged.emit()

    def setDefault(self):
        self._data = ZGlobal.styleDataManager.getStyleData(self._key)
        self.styleChanged.emit()

# import sys
# from PySide6.QtWidgets import QApplication
# from PySide6.QtGui import QColor
# from ZenWidgets.gui import ZButtonStyleData
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     logging.basicConfig(level=logging.INFO)
#     window = QWidget()
#     controller = StyleController[ZButtonStyleData](window, 'ZButton')
#     data = controller.data
#     data.Body = QColor(255, 0, 0)
#     print(data), print(controller._data)
#     window.show()
#     sys.exit(app.exec())
