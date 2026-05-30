import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets import *
from navigation_bar import NavigationBar
from panel_home import PanelHome
from panel_widget import PanelWidget
from panel_info import PanelInfo
from panel_window import PanelWindow
from panel_test import PanelTest
from panel_debug import PanelDebug
from panel_about import PanelAbout
from panel_settings import PanelSettings

class ZenUIGallery(ZStandardFramelessWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        #self.setMinimumSize(400, 300)
        screen_size = QGuiApplication.primaryScreen().size()
        self.resize(screen_size.width()*0.5,screen_size.height()*0.6)
        self.moveCenter()
        self.setWindowTitle("ZenWidgets Gallery")
        self.setWindowIcon(QIcon(":/image/icon.svg"))
        self.contentLayout = ZHBoxLayout(self.centerWidget())

        self.navigationBar = NavigationBar(self.centerWidget())
        self.contentLayout.addWidget(self.navigationBar, stretch=0)

        self.stackContainer = ZStackView(self.centerWidget())
        self.contentLayout.addWidget(self.stackContainer, stretch=1)

        self.panelHome = PanelHome(self.stackContainer)
        self.stackContainer.addWidget(self.panelHome)

        self.panelWidget = PanelWidget(self.stackContainer)
        self.stackContainer.addWidget(self.panelWidget)

        self.panelInfo = PanelInfo(self.stackContainer)
        self.stackContainer.addWidget(self.panelInfo)

        self.panelWindow = PanelWindow(self.stackContainer)
        self.stackContainer.addWidget(self.panelWindow)

        self.panelTest = PanelTest(self.stackContainer)
        self.stackContainer.addWidget(self.panelTest)

        self.panelDebug = PanelDebug(self.stackContainer)
        self.stackContainer.addWidget(self.panelDebug)

        self.panelAbout = PanelAbout(self.stackContainer)
        self.stackContainer.addWidget(self.panelAbout)

        self.pagelSettings = PanelSettings(self.stackContainer)
        self.stackContainer.addWidget(self.pagelSettings)

        self.navigationBar.getButton(0).clicked.connect(
            lambda: self.stackContainer.setCurrentWidget(self.panelHome)
            )
        self.navigationBar.getButton(1).clicked.connect(
            lambda: self.stackContainer.setCurrentWidget(self.panelWidget)
            )
        self.navigationBar.getButton(2).clicked.connect(
            lambda: self.stackContainer.setCurrentWidget(self.panelInfo)
            )
        self.navigationBar.getButton(3).clicked.connect(
            lambda: self.stackContainer.setCurrentWidget(self.panelWindow)
            )
        self.navigationBar.getButton(4).clicked.connect(
            lambda: self.stackContainer.setCurrentWidget(self.panelTest)
            )
        self.navigationBar.getButton(5).clicked.connect(
            lambda: self.stackContainer.setCurrentWidget(self.panelDebug)
            )
        self.navigationBar.getButton(6).clicked.connect(
            lambda: self.stackContainer.setCurrentWidget(self.panelAbout)
            )
        self.navigationBar.getButton(7).clicked.connect(
            lambda: self.stackContainer.setCurrentWidget(self.pagelSettings)
            )


if __name__ == '__main__':
    # enable dpi scale
    # QApplication.setHighDpiScaleFactorRoundingPolicy(
    #      Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    # app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    window = ZenUIGallery()
    window.show()
    app.exec()