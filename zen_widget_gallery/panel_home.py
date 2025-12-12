from PySide6.QtCore import Qt,QMargins
from PySide6.QtGui import QFont
from ZenWidgets import *
from rc_rc import *
class PanelHome(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelHome')
        self.setLayout(ZVBoxLayout(self,alignment=Qt.AlignmentFlag.AlignTop))
        self.image_bg = ZImage(parent=self,
                                  scale_type=ZImage.ScaleType.Fill,
                                  corner_radius=4)
        self.image_bg_mask = ZImage(parent=self,
                                  scale_type=ZImage.ScaleType.Stretch,
                                  corner_radius=4)
        ZGlobal.themeManager.themeChanged.connect(self._theme_changed_handler)
        self._load_bg_image()
        self._setup_ui()

    def _load_bg_image(self):
        if ZGlobal.themeManager.getTheme() == ZTheme.Light:
            self.image_bg.setImage(":/image/home_bg_light.svg")
            self.image_bg_mask.setImage(":/image/home_bg_mask_light.svg")
        else:
            self.image_bg.setImage(":/image/home_bg_dark.svg")
            self.image_bg_mask.setImage(":/image/home_bg_mask_dark.svg")


    def _theme_changed_handler(self, theme):
        self._load_bg_image()


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.image_bg.setGeometry(1, 1, self.width()-2, self.height()-2)
        self.image_bg_mask.setGeometry(1, 1, self.width()-2, self.height()-2)


    def _setup_ui(self):
        self.text_1 = ZHeadLine(self, text='Based on PySide6 -6.10.0')
        self.text_1.setFont(QFont('Microsoft YaHei', 11, QFont.Weight.Normal))
        self.text_1.setPadding(ZPadding(50,40,50,0))
        self.layout().addWidget(self.text_1)
        self.text_2 = ZHeadLine(self, text='ZenWidgets Gallery')
        self.text_2.setFont(QFont('Microsoft YaHei', 24, QFont.Weight.Bold))
        self.text_2.setPadding(ZPadding(50,0,50,0))
        self.layout().addWidget(self.text_2)