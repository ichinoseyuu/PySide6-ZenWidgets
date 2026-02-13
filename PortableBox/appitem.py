from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ZenWidgets import *
import os
import subprocess
import sys


class AppIconItemColorData(ZColorData):
    Text: QColor
    Body: QColor
    Border: QColor

colordata = {
    'Light': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.Body: lambda: ZPalette.Body,
        ZColorDataKey.Border: lambda: ZPalette.BorderNeutral
    },
    'Dark': {
        ZColorDataKey.Text: lambda: ZPalette.Text,
        ZColorDataKey.Body: lambda: ZPalette.Body,
        ZColorDataKey.Border: lambda: ZPalette.BorderNeutral
    }
}

@colordata_provider(datamap=colordata, classtype=AppIconItemColorData)
class AppIconItem(ZWidget):
    # 自定义信号，可选：向外暴露选中状态变化
    selectedChanged = Signal(bool)
    textColorCtrl: ZAnimatedColor
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    radiusCtrl: ZAnimatedFloat
    colorDataCtrl: ZColorController[AppIconItemColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'AppIconItem'},
        'radiusCtrl': {'value': 8.0}
    }
    def __init__(self, exe_path: str = "", parent=None):
        super().__init__(parent)
        # 基础属性
        self.exe_path = exe_path
        self.is_selected = False
        self.icon_pixmap = QPixmap()

        # 初始化大小（可根据需求调整）
        self.setFixedSize(64, 80)
        # 设置鼠标追踪和可点击
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)  # 支持焦点绘制选中框

        # 解析exe图标（如果路径有效）
        if exe_path and os.path.exists(exe_path):
            self._parse_exe_icon()
        self._init_color_data_()
        # 初始化右键菜单
        self._init_context_menu()

    def _init_color_data_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.color = data.Text
        self.borderColorCtrl.color = data.Border
        self.bodyColorCtrl.color = data.Body

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.borderColorCtrl.setColorTo(data.Border)
        self.textColorCtrl.setColorTo(data.Text)
        self.bodyColorCtrl.setColorTo(data.Body)

    def _init_style_(self):
        pass

    def _parse_exe_icon(self):
        """解析exe文件的图标并转换为QPixmap"""
        # Windows系统通过QFileIconProvider获取exe图标
        if sys.platform == "win32":
            icon_provider = QFileIconProvider()
            file_info = QFileInfo(self.exe_path)
            icon = icon_provider.icon(file_info)
            # 缩放图标到控件合适大小（预留文字空间，可调整）
            self.icon_pixmap = icon.pixmap(48, 48)
        else:
            # 非Windows系统占位图标（可自定义）
            standard_icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
            self.icon_pixmap = standard_icon.pixmap(48, 48)

    def _init_context_menu(self):
        self.context_menu = ZContextMenu(self)
        sub_actions = [
            ZAction("子项 1", callback=lambda: print("sub1")),
            ZAction("子项 2", callback=lambda: print("sub2"))
        ]
        sub_sub_actions = [
            ZAction("子子项 1", callback=lambda: self.show_exe_path()),
            ZAction("子子项 2", callback=lambda: print("sub-sub-2")),
        ]
        sub_actions2 = [
            ZAction("子项 带子菜单", submenu=sub_sub_actions,icon=ZGlobal.getBuiltinIcon(u':/icons/dark.svg')),
            ZAction("子项 2", callback=lambda: print("sub2"))
        ]
        item_1 = ZAction("打开应用(&O)", callback=self.open_exe)
        item_2 = ZAction("查看文件路径(&V)", callback=self.show_exe_path)
        item_3 = ZAction("更多(&M)", submenu=sub_actions)
        item_4 = ZAction("更多(&M)", submenu=sub_actions2)
        self.context_menu.addAction(item_1)
        self.context_menu.addAction(item_2)
        self.context_menu.addSeparator()
        self.context_menu.addAction(item_3)
        self.context_menu.addAction(item_4)

    def open_exe(self):
        """打开目标exe文件"""
        try:
            # 启动exe进程（不阻塞当前程序）
            subprocess.Popen([self.exe_path], shell=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开失败：{str(e)}")

    def show_exe_path(self):
        """显示exe文件路径的模态对话框"""
        # 创建对话框并持有引用，调用exec()弹出（模态，阻塞直到关闭）
        logging.info(f"显示路径对话框，当前exe路径：{self.exe_path}")

    def paintEvent(self, event: QPaintEvent):
        """手动绘制图标和选中框"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        radius = self.radiusCtrl.value
        # 1. 绘制选中框（外部框）
        if self.is_selected:
            painter.setPen(QPen(self.borderColorCtrl.color, 1, Qt.PenStyle.SolidLine))
            painter.setBrush(self.bodyColorCtrl.color)
            # 绘制外框，预留1px边距
            painter.drawRoundedRect(self.rect().adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        # 2. 绘制应用图标（居中）
        if not self.icon_pixmap.isNull():
            # 计算图标居中位置
            x = (self.width() - self.icon_pixmap.width()) // 2
            y = (self.height() - self.icon_pixmap.height()) // 2 - 5  # 稍微上移，预留文件名空间
            painter.drawPixmap(x, y, self.icon_pixmap)

        # 3. 绘制exe文件名（可选）
        if self.exe_path:
            file_name = os.path.basename(self.exe_path)
            painter.setPen(self.textColorCtrl.color)
            # 文字居中，在图标下方
            text_rect = QRect(0, self.height() - 20, self.width(), 20)
            painter.drawText(text_rect, Qt.AlignCenter, file_name[:8] + "..." if len(file_name) > 8 else file_name)

    def mousePressEvent(self, event: QMouseEvent):
        """单击事件：切换选中状态"""
        if event.button() == Qt.LeftButton:
            self.is_selected = not self.is_selected
            self.selectedChanged.emit(self.is_selected)
            self.update()  # 重绘选中框
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击事件：打开exe文件"""
        if event.button() == Qt.LeftButton and self.exe_path and os.path.exists(self.exe_path):
            self.open_exe()
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.context_menu.showAt(event.globalPos())
        super().contextMenuEvent(event)



# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建主窗口
    main_win = QMainWindow()
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    main_win.setCentralWidget(central_widget)

    # 创建自定义控件（示例：传入记事本exe路径）
    notepad_path = "C:/Windows/System32/notepad.exe"  # Windows记事本路径
    app_icon = AppIconItem(notepad_path)

    # 选中状态变化示例
    app_icon.selectedChanged.connect(lambda is_selected: print(f"选中状态：{is_selected}"))

    layout.addWidget(app_icon, alignment=Qt.AlignCenter)
    main_win.resize(200, 200)
    main_win.show()

    sys.exit(app.exec())