from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout,QSizePolicy,QLabel
from PySide6.QtCore import Qt, QMargins,QPoint,QSize
from PySide6.QtGui import QFont, QIcon, QColor
from ZenWidgets import *
import random

class PanelWidget(ZPanel):
    def __init__(self, parent = None):
        super().__init__(parent, objectName ='PanelWidget')
        self.setLayout(ZVBoxLayout(self, QMargins(0, 0, 0, 0), 0, Qt.AlignmentFlag.AlignTop))
        self._setup_ui()

    def _setup_ui(self):
        # scrollview.layout().setExpand(True)
        scrollview = ZScrollView(self)
        scrollview.setLayout(ZVBoxLayout(scrollview, QMargins(40, 30, 40, 30), 30, Qt.AlignmentFlag.AlignTop))
        self.layout().addWidget(scrollview)

        title = ZHeadLine(self, text='基础组件', display_indicator=True)
        title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))
        title.setPadding(ZPadding(6, 6, 6, 6))
        scrollview.layout().addWidget(title)

        title = ZHeadLine(self, text= '基本输入组件', display_indicator=True)
        title.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        title.setPadding(ZPadding(6, 6, 6, 6))
        scrollview.layout().addWidget(title)

        flowcont = ZFlowContainer(self)
        flowcont.setLineHeight(100)
        scrollview.layout().addWidget(flowcont)

        # region ZButton
        card = ZCard(self)
        flowcont.addWidget(card)

        title = ZHeadLine(card, text= 'ZButton')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZHContainer(card)
        card.layout().addWidget(container)

        btn_icon = ZGlobal.iconPack.toIcon('ic_fluent_save_regular')
        self.btn_1 = ZButton(container, icon=btn_icon, style=ZButtonStyle.Flat)
        container.addWidget(self.btn_1, spacing=16)
        self.btn_1.clicked.connect(
            lambda: ZGlobal.tooltip.showTip(
                text='保存成功',
                target=self.btn_1,
                mode=ZToolTip.Mode.TrackTarget,
                position=ZPosition.Top,
                offset=QPoint(0, 6),
                hide_delay=800
                )
            )

        self.btn_2 = ZButton(container, text='保存', style=ZButtonStyle.Flat)
        container.addWidget(self.btn_2, spacing=16)
        self.btn_2.clicked.connect(
            lambda: ZGlobal.tooltip.showTip(
                text='保存成功',
                target=self.btn_2,
                mode=ZToolTip.Mode.TrackTarget,
                position=ZPosition.Top,
                offset=QPoint(0, 6),
                hide_delay=800
                )
            )

        self.btn_3 = ZButton(container, icon=btn_icon, text='保存', style=ZButtonStyle.Flat)
        container.addWidget(self.btn_3, spacing=16)
        self.btn_3.clicked.connect(
            lambda: ZGlobal.tooltip.showTip(
                text='保存成功',
                target=self.btn_3,
                mode=ZToolTip.Mode.TrackTarget,
                position=ZPosition.Top,
                offset=QPoint(0, 6),
                hide_delay=800
                )
            )

        self.btn_4 = ZButton(container, icon=btn_icon)
        container.addWidget(self.btn_4, spacing=16)
        self.btn_4.clicked.connect(
            lambda: ZGlobal.tooltip.showTip(
                text='保存成功',
                target=self.btn_4,
                mode=ZToolTip.Mode.TrackTarget,
                position=ZPosition.Top,
                offset=QPoint(0, 6),
                hide_delay=800
                )
            )

        self.btn_5 = ZButton(container, icon=btn_icon, text='保存')
        container.addWidget(self.btn_5, spacing=16)
        self.btn_5.clicked.connect(
            lambda: ZGlobal.tooltip.showTip(
                text='保存成功',
                target=self.btn_5,
                mode=ZToolTip.Mode.TrackTarget,
                position=ZPosition.Top,
                offset=QPoint(0, 6),
                hide_delay=800
                )
            )

        self.btn_6 = ZButton(container, text='保存')
        container.addWidget(self.btn_6, spacing=16)
        self.btn_6.clicked.connect(
            lambda: ZGlobal.tooltip.showTip(
                text='保存成功',
                target=self.btn_6,
                mode=ZToolTip.Mode.TrackTarget,
                position=ZPosition.Top,
                offset=QPoint(0, 6),
                hide_delay=800
                )
            )

        # region ZToggleButton
        card = ZCard(self)
        flowcont.addWidget(card)

        title = ZHeadLine(card, text= 'ZToggleButton')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZHContainer(card)
        card.layout().addWidget(container)

        self.toggle_btn_1 = ZToggleButton(container, icon=btn_icon, style=ZButtonStyle.Flat)
        container.addWidget(self.toggle_btn_1, spacing=16)

        self.toggle_btn_2 = ZToggleButton(container, text='自动保存', style=ZButtonStyle.Flat)
        container.addWidget(self.toggle_btn_2, spacing=16)

        self.toggle_btn_3 = ZToggleButton(container, icon=btn_icon, text='自动保存', style=ZButtonStyle.Flat)
        container.addWidget(self.toggle_btn_3, spacing=16)

        self.toggle_btn_4 = ZToggleButton(container, icon=btn_icon)
        self.toggle_btn_4.setToolTip('自动保存')
        container.addWidget(self.toggle_btn_4, spacing=16)

        self.toggle_btn_5 = ZToggleButton(container, icon=btn_icon, text='自动保存')
        container.addWidget(self.toggle_btn_5, spacing=16)

        self.toggle_btn_6 = ZToggleButton(container, text='自动保存')
        container.addWidget(self.toggle_btn_6, spacing=16)

        # region ZRepeatButton
        card = ZCard(self)
        flowcont.addWidget(card)

        title = ZHeadLine(card, text= 'ZRepeatButton')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZHContainer(card)
        card.layout().addWidget(container)

        info_repeat = ZHeadLine(container, text= '连续点击次数: 0')
        container.addWidget(info_repeat)

        self.repeat_btn_1 = ZRepeatButton(container, text='长按连点',style=ZButtonStyle.Flat)
        container.addWidget(self.repeat_btn_1)
        self.repeat_btn_1.clicked.connect(
            lambda: info_repeat.setText(f'连续点击次数: {self.repeat_btn_1.repeatCount()}',flash=True)
            )

        self.repeat_btn_2 = ZRepeatButton(container, text='长按连点')
        container.addWidget(self.repeat_btn_2)
        self.repeat_btn_2.clicked.connect(
            lambda: info_repeat.setText(f'连续点击次数: {self.repeat_btn_2.repeatCount()}',flash=True)
            )

        # region ZLongPressButton
        card = ZCard(self)
        flowcont.addWidget(card)

        title = ZHeadLine(card, text= 'ZLongPressButton')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZHContainer(card)
        card.layout().addWidget(container)

        info_confirm = ZHeadLine(container, text= '是否删除')
        container.addWidget(info_confirm)

        self.long_press_btn_1 = ZLongPressButton(container, text='长按以确认')
        container.addWidget(self.long_press_btn_1)
        self.long_press_btn_1.longPressClicked.connect(
            lambda: info_confirm.setText(f'删除成功', flash=True)
            )

        # region ZProgressButton
        card = ZCard(self)
        flowcont.addWidget(card)

        title = ZHeadLine(card, text= 'ZProgressButton')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZHContainer(card)
        card.layout().addWidget(container)

        info_progress = ZHeadLine(container, text= '进度: 0 %')
        # 固定进度文本宽度，防止文字变长时推动按钮位置
        fm = info_progress.fontMetrics()
        max_text = '进度: 100.00 %'
        fixed_w = fm.horizontalAdvance(max_text) + info_progress.padding().horizontal() + 8
        info_progress.setFixedWidth(fixed_w)
        container.addWidget(info_progress)

        self.progress_btn = ZProgressButton(card, text="随机进度")
        self.progress_btn.clicked.connect(lambda: self.progress_btn.setProgress(random.random()))
        self.progress_btn.progressChanged.connect(lambda x: info_progress.setText(f"进度: {x*100:.2f} %",flash=True))
        container.addWidget(self.progress_btn)

        # region ZSwitch
        card = ZCard(self)
        flowcont.addWidget(card)

        title = ZHeadLine(card, text= 'ZSwitch')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZHContainer(card)
        container.setAlignment(Qt.AlignmentFlag.AlignBottom)
        card.layout().addWidget(container)

        self.switch_1 = ZSwitch(container, style= ZSwitchStyle.Compact)
        container.addWidget(self.switch_1, spacing=16)

        self.switch_2 = ZSwitch(container, style= ZSwitchStyle.Standard)
        container.addWidget(self.switch_2, spacing=16)

        self.switch_3 = ZSwitch(container, style= ZSwitchStyle.Comfortable)
        container.addWidget(self.switch_3, spacing=16)

        # region ZComboBox
        card = ZCard(self)
        flowcont.addWidget(card)

        title = ZHeadLine(card, text= 'ZComboBox')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZVContainer(card)
        card.layout().addWidget(container)


        options = ['坤坤', '凡凡', '祺祺', '鑫鑫']
        self.combo_box_1 = ZComboBox(self, text='请选择')
        self.combo_box_1.addOptions(options)
        container.addWidget(self.combo_box_1)

        flowcont.adjustSize()
        flowcont.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        # 或更稳：flowcont.setFixedHeight(flowcont.height())

        # region ZSlider
        card = ZCard(self)
        scrollview.layout().addWidget(card)

        title = ZHeadLine(card, text= 'ZSlider')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        hlayout = ZHBoxLayout(
            margins=QMargins(0, 0, 0, 0),
            spacing=16,
            alignment=Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignCenter
            )
        card.layout().addLayout(hlayout)

        container1 = ZVContainer(card)
        container1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container1.setSpacing(16)
        hlayout.layout().addWidget(container1)

        self.hslider_1 = ZSlider(
            parent=container1,
            direction=ZDirection.Horizontal,
            style=ZSliderStyle.Thin,
            scope=(0, 10),
            step=0.5,
            accuracy=0.1,
            value=5,
            length=300
            )
        container1.addWidget(self.hslider_1)

        self.hslider_2 = ZSlider(
            parent=container1,
            direction=ZDirection.Horizontal,
            style=ZSliderStyle.Default,
            scope=(0, 100),
            step=1,
            accuracy=1,
            value=50,
            length=300
            )
        container1.addWidget(self.hslider_2)

        self.hslider_3 = ZSlider(
            parent=container1,
            direction=ZDirection.Horizontal,
            style=ZSliderStyle.Thick,
            scope=(0, 100),
            step=0.5,
            accuracy=0.1,
            value=50,
            auto_strip_zero=True,
            length=300
            )
        container1.addWidget(self.hslider_3)

        container2 = ZHContainer(card)
        container2.setAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        container2.setSpacing(16)
        hlayout.layout().addWidget(container2)

        self.vslider_1 = ZSlider(
            parent=container2,
            direction=ZDirection.Vertical,
            style=ZSliderStyle.Thin,
            scope=(0, 10),
            step=0.5,
            accuracy=0.1,
            value=5
            )
        container2.addWidget(self.vslider_1)

        self.vslider_2 = ZSlider(
            parent=container2,
            direction=ZDirection.Vertical,
            style=ZSliderStyle.Default,
            scope=(0, 100),
            step=1,
            accuracy=1,
            value=50
            )
        container2.addWidget(self.vslider_2)

        self.vslider_3 = ZSlider(
            parent=container2,
            direction=ZDirection.Vertical,
            style=ZSliderStyle.Thick,
            scope=(0, 100),
            step=0.5,
            accuracy=0.1,
            value=50
            )
        container2.addWidget(self.vslider_3)


        # region ZHeadLine
        title = ZHeadLine(self, text= '文本显示组件', display_indicator=True)
        title.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        title.setPadding(ZPadding(6, 6, 6, 6))
        scrollview.layout().addWidget(title)

        card = ZCard(self)
        scrollview.layout().addWidget(card)

        title = ZHeadLine(card, text= 'ZHeadLine')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZHContainer(card)
        card.layout().addWidget(container)

        self.headline_1 = ZHeadLine(container)
        self.headline_1.setText('标题')
        container.addWidget(self.headline_1)

        self.headline_2 = ZHeadLine(container, display_indicator=True)
        self.headline_2.setText('带指示器的标题')
        container.addWidget(self.headline_2)

        self.headline_3 = ZHeadLine(container, selectable=True)
        self.headline_3.setText('可选中的标题')
        container.addWidget(self.headline_3)

        # region ZTextBlock
        card = ZCard(self)
        scrollview.layout().addWidget(card)

        title = ZHeadLine(card, text= 'ZTextBlock')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZVContainer(card)
        card.layout().addWidget(container)

        text= '''ZenWidgets 是一款为追求极致用户体验的开发者打造的现代化风格的组件库，它基于 PySide6 中的 QWidget 架构设计而成，在保持界面简洁的同时，融入了流畅的交互动画。与 QWidget 不同，ZenWidgets 支持动态切换主题和自定义主题配色，通过舍弃对 QSS 样式表的依赖，采用完全自定义的绘制逻辑，让UI具有流畅的交互动画且风格更符合现代审美。目前，ZenWidgets 已提供覆盖基础界面开发需求的核心组件。ZenWidgets 组件库正处于持续进化中，未来计划加入更多实用模块，致力于为 PySide6 开发者提供一套既美观又高效的界面解决方案，在 QWidget 界面开发上变得更简单快捷。'''

        self.textblock_1 = ZTextBlock(container, text=text, selectable=True)
        self.textblock_1.resize(600, 400)
        container.addWidget(self.textblock_1)

        self.textblock_2 = ZTextBlock(container, text=text, selectable=True)
        self.textblock_2.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.textblock_2.resize(600, 400)
        container.addWidget(self.textblock_2)
        #card.layout().addWidget(self.textblock_2)


        # region ZLineEdit
        card = ZCard(self)
        scrollview.layout().addWidget(card)

        card.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        title = ZHeadLine(card, text= 'ZLineEdit')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZVContainer(card)
        card.layout().addWidget(container)

        self.lineedit_1 = ZLineEdit(
            parent=container,
            minimumSize=QSize(300, 30)
        )
        container.addWidget(self.lineedit_1)

        self.lineedit_2 = ZLineEdit(
            parent=container,
            placeholder='带有提示文字的编辑框',
            minimumSize=QSize(300, 30)
        )
        container.addWidget(self.lineedit_2)

        self.lineedit_3 = ZLineEdit(
            parent=container,
            text='不能修改的编辑框',
            read_only=True,
            selectable=False,
            minimumSize=QSize(300, 30)
        )
        container.addWidget(self.lineedit_3)

        self.lineedit_4 = ZLineEdit(
            parent=container,
            text='不能修改但可以选中编辑框',
            read_only=True,
            selectable=True,
            minimumSize=QSize(300, 30)
        )
        container.addWidget(self.lineedit_4)

        # region ZLoginEdit
        card = ZCard(self)
        scrollview.layout().addWidget(card)

        title = ZHeadLine(card, text= 'ZLoginEdit')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZVContainer(card)
        card.layout().addWidget(container)

        container_sub = ZHContainer(container)
        container.addWidget(container_sub)

        title_account = ZHeadLine(card, text= '账号:')
        container_sub.addWidget(title_account)

        self.login_edit_1 = ZLoginEdit(card, allow_characters=False)
        container_sub.addWidget(self.login_edit_1)

        container_sub = ZHContainer(container)
        container.addWidget(container_sub)

        title_password = ZHeadLine(card, text= '密码:')
        container_sub.addWidget(title_password)

        self.login_edit_2 = ZLoginEdit(card, is_masked=True)
        container_sub.addWidget(self.login_edit_2)

        # region ZNumberEdit
        card = ZCard(self)
        scrollview.layout().addWidget(card)

        title = ZHeadLine(card, text= 'ZNumberEdit')
        title.setFont(QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        card.layout().addWidget(title)

        container = ZVContainer(card)
        card.layout().addWidget(container)
        self.number_edit_1 = ZNumberEdit(card)
        container.addWidget(self.number_edit_1)

        self.number_edit_2 = ZNumberEdit(card, allow_negative=True, allow_decimal=True)
        container.addWidget(self.number_edit_2)