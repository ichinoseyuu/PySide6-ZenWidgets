from PySide6.QtWidgets import QWidget,QSizePolicy
from PySide6.QtCore import Qt,QRectF,QSize,QRect,QMargins,QPoint,Signal,QEventLoop
from PySide6.QtGui import QPainter,QPen,QColor,QFont
from ZenWidgets.component.input import ZButton,ZLongPressButton
from ZenWidgets.component.layouts import ZVBoxLayout
from ZenWidgets.component.base import(
    ZWidget,
    ZContentWidget,
    ZAnimatedColor,
    ZAnimatedFloat,
    ZColorController
)
from ZenWidgets.component.text import ZHeadLine,ZTextBlock
from ZenWidgets.core import ZMargins,ZDebug
from ZenWidgets.gui import ZWidgetEffect,ZDialogColorData

#region ZDialog
class ZDialog(ZWidget):
    Accepted = 1
    Rejected = 0
    finished = Signal(int)

    bodyColorCtrl: ZAnimatedColor
    footerColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[ZDialogColorData]
    __controllers_kwargs__ = {
        'radiusCtrl': {'value': 5.0},
        'colorDataCtrl': {'key': 'ZDialog'}
    }
    def __init__(self,
                 parent: ZWidget | None = None,
                 title: str = '标题',
                 message: str = '消息',
                 inject: str = '取消',
                 accept: str = '确定',
                 have_long_press_btn: bool = False,
                 long_press: str = '长按以确认'
                 ):
        super().__init__(parent=parent, f=Qt.WindowType.FramelessWindowHint|Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowModal)
        self.windowOpacityCtrl.completelyHide.connect(self.hide)
        self._margin = ZMargins(8, 8, 8, 8)

        self._result = self.Rejected


        self._content = ZContentWidget(self)
        self._content.move(self._margin.left, self._margin.top)
        self._content.setLayout(ZVBoxLayout(self._content, spacing=6, margins=QMargins(6, 6, 6, 6)))

        self._title = ZHeadLine(self._content, text=title, display_indicator=True, font=QFont('Microsoft YaHei', 10, QFont.Weight.Bold))
        self._content.layout().addWidget(self._title, stretch=0)

        self._message = ZTextBlock(self._content, text=message,height_for_width=False)
        self._message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._content.layout().addWidget(self._message, stretch=1)

        self._footer = ZContentWidget(self)
        self._footer.setLayout(ZVBoxLayout(self._footer, spacing=6, margins=QMargins(6, 6, 6, 6)))

        self._btn_long_press = ZLongPressButton(self._footer, text=long_press)
        self._btn_long_press.setFixedHeight(40)
        self._footer.layout().addWidget(self._btn_long_press)
        self._btn_long_press.setVisible(have_long_press_btn)
        self._btn_long_press.longPressClicked.connect(self.accept)

        self._btn_accept = ZButton(self._footer, text=accept, sizePolicy=QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self._btn_accept.setFixedHeight(40)
        self._btn_accept.clicked.connect(self.accept)
        self._footer.layout().addWidget(self._btn_accept)

        self._btn_reject = ZButton(self._footer, text=inject, sizePolicy=QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self._btn_reject.setFixedHeight(40)
        self._btn_reject.clicked.connect(self.reject)
        self._footer.layout().addWidget(self._btn_reject)
        self._content.layout().addWidget(self._footer, stretch=0)

        self.windowOpacityCtrl.completelyHide.connect(self.close)
        self._init_color_data_()

    # private
    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.color = data.Body
        self.footerColorCtrl.color = data.RegionFooter
        self.borderColorCtrl.color = data.Border

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.bodyColorCtrl.setColorTo(data.Body)
        self.footerColorCtrl.setColorTo(data.RegionFooter)
        self.borderColorCtrl.setColorTo(data.Border)

    def accept(self):
        self._result = self.Accepted
        self.windowOpacityCtrl.fadeOut()
        self.finished.emit(self._result)

    def reject(self):
        self._result = self.Rejected
        self.windowOpacityCtrl.fadeOut()
        self.finished.emit(self._result)

    def exec(self):
        self._result = self.Rejected
        self.show()
        loop = QEventLoop(self)
        self.finished.connect(loop.quit)
        loop.exec()
        return self._result

    def result(self): return self._result

    def show(self):
        super().show()
        size = self.sizeHint()
        self.resize(size)
        center = self.parentWidget().window().geometry().center() if self.parentWidget() else self.screen().geometry().center()
        self.move(center.x() - size.width() // 2, center.y() - size.height() // 2)
        self.windowOpacityCtrl.fadeTo(.0,1.0)
        self.raise_()

    def sizeHint(self):
        layout_size = self._content.layout().sizeHint() + self._margin.size()
        dpr = self.screen().devicePixelRatio() if self.screen() else 1.0
        base_min_width = 400
        base_min_height = 300

        min_width = max(round(base_min_width * dpr), layout_size.width())
        min_height = max(round(base_min_height * dpr), layout_size.height())

        return QSize(min_width, min_height)

    # event
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._content.resize(event.size() - self._margin.size())

    def closeEvent(self, event):
        if self._result not in (self.Accepted, self.Rejected):
            self._result = self.Rejected
            self.finished.emit(self._result)
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, event):
        if self.opacityCtrl.opacity == 0: return
        painter = QPainter(self)
        painter.setOpacity(self.opacityCtrl.opacity)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self._content.geometry())
        border_rect = QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = self.radiusCtrl.value

        ZWidgetEffect.drawGraphicsShadow(painter, rect, radius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRoundedRect(rect, radius, radius)

        painter.setPen(QPen(self.borderColorCtrl.color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(border_rect, radius, radius)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        event.accept()



if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    # 14. QDialog 风格调用方式（阻塞式，直接通过返回值判断结果）
    dialog = ZDialog(
        title="确认操作",
        message="是否要执行此操作？",
        confirm="执行",
        cancel="取消",
        have_long_press_btn=True,
        long_press="长按强制执行"
    )

    # 无需调用 show()，直接用 exec() 获取结果
    result = dialog.exec()

    # 根据结果码处理逻辑
    if result == ZDialog.Accepted:
        print("用户确认：执行操作")
    else:
        print("用户取消：终止操作")

    # 多次复用示例（直接再次调用 exec() 即可）
    # result2 = dialog.exec()
    # if result2 == ZDialog.Accepted:
    #     print("第二次确认")

    sys.exit(app.exec())
