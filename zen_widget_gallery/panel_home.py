from PySide6.QtCore import Qt,QMargins
from PySide6.QtGui import QFont
from ZenWidgets import *
from card_weblink import CardWebLink
from rc_rc import *
class PanelHome(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelHome')
        self.setLayout(ZVBoxLayout(self,margins=QMargins(1,1,1,1),alignment=Qt.AlignmentFlag.AlignTop))
        self.image_bg = ZImage(parent=self,
                                  scale_type=ZImage.ScaleType.Fill,
                                  corner_radius=4)
        ZGlobal.themeManager.themeChanged.connect(self._theme_changed_handler)
        self._load_bg_image()
        self._setup_ui()

    def _load_bg_image(self):
        if ZGlobal.themeManager.getTheme() == ZTheme.Light:
            self.image_bg.setImage(":/image/home_bg_light.svg")
        else:
            self.image_bg.setImage(":/image/home_bg_dark.svg")


    def _theme_changed_handler(self, theme):
        self._load_bg_image()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.image_bg.setGeometry(1, 1, self.width()-2, 400)

    def _setup_ui(self):
        scrollview = ZScrollView(self)
        scrollview.setLayout(ZVBoxLayout(scrollview, margins=QMargins(0,0,0,0), alignment=Qt.AlignmentFlag.AlignTop))
        self.layout().addWidget(scrollview)
        text_1 = ZHeadLine(scrollview, text='Based on PySide6 -6.10.1')
        text_1.setFont(QFont('Microsoft YaHei', 11, QFont.Weight.Normal))
        text_1.setPadding(ZPadding(30,40,50,0))
        scrollview.layout().addWidget(text_1)
        text_2 = ZHeadLine(scrollview, text='ZenWidgets Gallery')
        text_2.setFont(QFont('Microsoft YaHei', 24, QFont.Weight.Bold))
        text_2.setPadding(ZPadding(30,0,50,0))
        scrollview.layout().addWidget(text_2)
        scrollview.layout().addSpacerItem(ZVSpacerItem(140).setExpanding(vertical=False))
        cardlist = ZHListView(scrollview,margins=QMargins(0,0,0,0),spacing=10,show_handle=False)
        cardlist.setFixedHeight(170)
        scrollview.layout().addWidget(cardlist)
        cardlist.layout().addSpacerItem(ZHSpacerItem(30).setExpanding(horizontal=False))
        cardlist.layout().addWidget(
            CardWebLink(
                cardlist,
                title='ZenWidgets on Github',
                description='Explore the source code and contribute to the project',
                icon=':/image/other/github.svg',
                url='https://github.com/ichinoseyuu/PySide6-ZenWidgets'
                )
            )
        cardlist.layout().addWidget(
            CardWebLink(
                cardlist,
                title='Code Samples',
                description='Find code snippets and examples to help you get started quickly',
                icon=':/image/other/Python.svg',
                url=''
                )
            )
        cardlist.layout().addSpacerItem(ZHSpacerItem(30))
        scrollview.layout().addSpacerItem(ZVSpacerItem(120))
        pass