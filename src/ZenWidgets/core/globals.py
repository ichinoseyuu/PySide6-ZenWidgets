from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ZenWidgets.component.info import ZToolTip
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtGui import QIcon,QCursor
from ZenWidgets.core.debug import ZDebug
from ZenWidgets.gui import ZThemeManager,ZIconPack,ZPalette,ZStyleDataManager

__All__ = ['ZGlobal']

class ZGlobal(object):
    tooltip: 'ZToolTip' = None
    themeManager = ZThemeManager()
    iconPack = ZIconPack()
    palette = ZPalette
    styleDataManager = ZStyleDataManager()

    @staticmethod
    def getBuiltinIcon(icon_path: str) -> QIcon:
        """获取内置资源中的图标"""
        return QIcon(icon_path)

    @staticmethod
    def getMouseTopWidget() -> QWidget | None:
        """获取鼠标当前位置的顶层可见Widget"""
        return QApplication.widgetAt(QCursor.pos())

    @classmethod
    def initZenWidgets(cls):
        ZDebug._init_logging_()
        theme = cls.themeManager.getThemeName()
        if theme == 'Dark':
            ZPalette.loadDarkPalette()
        else:
            ZPalette.loadLightPalette()

ZGlobal.initZenWidgets()