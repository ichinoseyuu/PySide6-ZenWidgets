from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout,QSizePolicy
from PySide6.QtCore import Qt, QMargins,QPoint,QMarginsF,QSize
from PySide6.QtGui import QFont, QIcon, QColor
from ZenWidgets import *

class PanelTest(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelTest')
        self.setLayout(ZVBoxLayout(self, QMargins(40, 30, 40, 30), 30, Qt.AlignmentFlag.AlignTop))
        self._setup_ui()


    def _setup_ui(self):
        self.title = ZHeadLine(self, text='测试组件', display_indicator=True)
        self.title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))
        self.title.setPadding(ZPadding(6, 0, 6, 6))
        self.layout().addWidget(self.title)

        # flowlayout = ZFlowLayout(animate=True)
        # flowlayout.setLineHeight(64)
        # self.layout().addLayout(flowlayout)

        # i = 0
        # for icon_name, pixmap in ZGlobal.iconPack.icons(size=QSize(64, 64)):
        #     if i > 40: break
        #     #print(f"图标名称: {icon_name}")
        #     m = ZImage(self)
        #     m.resize(pixmap.size())
        #     m.setPixmap(pixmap)
        #     flowlayout.addWidget(m)
        #     i += 1
        container = ZFlowContainer(self)
        self.layout().addWidget(container)
        container.setLineHeight(64)
        i = 0
        for _, pixmap in ZGlobal.iconPack.icons(size=QSize(64, 64)):
            if i > 20: break
            #print(f"图标名称: {icon_name}")
            m = ZImage(container)
            m.resize(pixmap.size())
            m.setPixmap(pixmap)
            container.addWidget(m)
            container.regDraggableWidget(m)
            i += 1

        split = ZHSplitView(self,initial_ratios=[0.25, 0.75])

        left_panel = ZVListView(split)
        for i in range(1, 50):
            btn = ZButton(left_panel, text=f"Item {i}")
            left_panel.layout().addWidget(btn)

        # 右侧为一个竖直三分的嵌套 SplitView
        right_nested = ZVSplitView(split,initial_ratios=[0.4, 0.3, 0.3])

        rp1 = ZPanel(right_nested)
        l1 = ZVBoxLayout(rp1, alignment=Qt.AlignmentFlag.AlignTop)
        l1.addWidget(ZHeadLine(rp1, text='Top Pane'))

        rp2 = ZVListView(right_nested)
        for i in range(1, 50):
            rp2.layout().addWidget(ZButton(rp2, text=f"Sub {i}"))

        rp3 = ZPanel(right_nested)
        l3 = ZVBoxLayout(rp3, alignment=Qt.AlignmentFlag.AlignTop)
        l3.addWidget(ZHeadLine(rp3, text='Bottom Pane'))

        right_nested.setWidgets(rp1, rp2, rp3)

        split.setWidgets(left_panel, right_nested)
        # 不固定高度/宽度，依赖布局自适应
        split.setFixedHeight(500)
        self.layout().addWidget(split)
        # container = ZFlowContainer(self)
        # self.content().layout().addWidget(container)
        # # container.setColumns(3)
        # # container.setColumnWidth(100)
        # # container.setAutoAdjustColumnAmount(True)
        # container.setLineHeight(64)
        # i = 0
        # for icon_name, pixmap in ZGlobal.iconPack.icons(size=QSize(64, 64)):
        #     if i > 20: break
        #     #print(f"图标名称: {icon_name}")
        #     m = ZImage(container)
        #     m.resize(pixmap.size())
        #     m.setPixmap(pixmap)
        #     container.addWidget(m)
        #     container.regDraggableWidget(m)
        #     i += 1

        # card1 = ZNewCard(self)
        # card1.container().setObjectName('par')
        # self.content().layout().addWidget(card1)
        # card1.container().addWidget(ZHeadLine(card1, text='尺寸变化测试'))
        # container1 = ZHContainer(card1,objectName='sub')
        # card1.container().addWidget(container1)
        # text = ZHeadLine(container1, text='测试文本')
        # container1.addWidget(text)
        # btn = ZButton(container1, text='按钮')
        # container1.addWidget(btn)
        # btn.clicked.connect(lambda: text.setText('按钮被点击按钮被点击按钮被点击'))