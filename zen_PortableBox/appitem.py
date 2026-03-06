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
class AppIconItem(ZToggleWidget):
    textColorCtrl: ZAnimatedColor
    bodyColorCtrl: ZAnimatedColor
    borderColorCtrl: ZAnimatedColor
    colorDataCtrl: ZColorController[AppIconItemColorData]
    __controllers_kwargs__ = {
        'colorDataCtrl':{'key': 'AppIconItem'}
    }
    def __init__(self,
                 parent: QWidget | None = None,
                 exe_path: str = "",
                 app_name: str = "",
                 font: QFont = QFont('Microsoft YaHei', 8)
                 ):
        super().__init__(parent=parent,
                         font=font
                         )
        # 设置鼠标追踪和可点击
        #self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)  # 支持焦点绘制选中框
        # 基础属性
        self._exe_path = exe_path
        self._app_name = app_name if app_name else os.path.basename(exe_path) if exe_path else "Unknown App"
        self._icon_pixmap = QPixmap()
        self._icon_size = QSize(32, 32)  # 图标显示大小（可调整）
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
        self.borderColorCtrl.transparent()
        if self._checked:
            self.bodyColorCtrl.color = data.Body
        else:
            self.bodyColorCtrl.color = data.Body
            self.bodyColorCtrl.transparent()

    def _color_data_change_handler_(self):
        data = self.colorDataCtrl.data
        self.textColorCtrl.setColorTo(data.Text)
        self.borderColorCtrl.color = data.Border
        self.borderColorCtrl.transparent()
        if self._checked:
            self.bodyColorCtrl.setColorTo(data.Body)
        else:
            self.bodyColorCtrl.setColor(data.Body)
            self.bodyColorCtrl.transparent()

    def _init_style_(self):
        pass

    def _mouse_enter_(self):
        self.borderColorCtrl.toOpaque()

    def _mouse_leave_(self):
        self.borderColorCtrl.toTransparent()

    def _toggle_(self):
        if self._checked:
            self.bodyColorCtrl.toOpaque()
        else:
            self.bodyColorCtrl.toTransparent()

    def _parse_exe_icon(self):
        """解析exe文件的图标并转换为QPixmap"""
        # Windows系统通过QFileIconProvider获取exe图标
        if sys.platform == "win32":
            icon_provider = QFileIconProvider()
            file_info = QFileInfo(self._exe_path)
            icon = icon_provider.icon(file_info)
            # 缩放图标到控件合适大小（预留文字空间，可调整）
            self._icon_pixmap = icon.pixmap(32, 32)
        else:
            # 非Windows系统占位图标（可自定义）
            standard_icon = QApplication.style().standardIcon(QStyle.SP_FileIcon)
            self._icon_pixmap = standard_icon.pixmap(48, 48)

    def _init_context_menu(self):
        self.context_menu = ZContextMenu(self)
        item_1 = ZAction("打开应用(&O)", callback=self.open_exe)
        item_2 = ZAction("查看文件路径(&V)", callback=lambda: print(f"File path: {self._exe_path}"))
        item_3 = ZAction("在资源管理器中打开(&O)", callback=lambda: print("Opening in Explorer"))
        item_4 = ZAction("在PortableBox中删除(&D)", callback=lambda: print("Deleting app"))
        self.context_menu.addAction(item_1)
        self.context_menu.addAction(item_2)
        self.context_menu.addAction(item_3)
        self.context_menu.addAction(item_4)

    def open_exe(self):
        """打开目标exe文件"""
        try:
            # 启动exe进程（不阻塞当前程序）
            subprocess.Popen([self._exe_path], shell=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开失败：{str(e)}")

    def sizeHint(self):
        """建议大小：根据图标和文字预设一个合理的尺寸"""
        width = self._icon_size.width() + 36 # 图标宽度+边距，最小80
        height = self._icon_size.height() + 42 # 图标高度+文字空间
        return QSize(width, height)


    def paintEvent(self, event: QPaintEvent):
        """手动绘制图标和选中框（优化圆角抗锯齿）"""
        painter = QPainter(self)
        # 1. 强化抗锯齿：画家+画笔双重抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)  # 画家抗锯齿
        painter.setRenderHint(QPainter.SmoothPixmapTransform)  # 图标绘制也平滑
        rect = self.rect()

        # 2. 绘制选中框（外部框）- 优化核心：分离边框和背景，像素对齐+圆角画笔
        pen = QPen(self.borderColorCtrl.color, 1, Qt.PenStyle.SolidLine)  # 宽度设为0
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(self.bodyColorCtrl.color)
        painter.drawRect(rect)

        if not self._icon_pixmap.isNull():
            icon_pos = self.rect().center() - QPoint(self._icon_size.width()/2, self._icon_size.height()/2 + 4)
            painter.drawPixmap(icon_pos, self._icon_pixmap)

        if self._exe_path:
            file_name = self._app_name
            painter.setPen(self.textColorCtrl.color)
            text_rect = QRect(0, self.height() - 20, self.width(), 20)
            # 文字也可开启平滑绘制
            painter.setRenderHint(QPainter.TextAntialiasing)
            painter.drawText(text_rect, Qt.AlignCenter, file_name[:10] + "..." if len(file_name) > 10 else file_name)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """双击事件：打开exe文件"""
        if event.button() == Qt.LeftButton and self._exe_path and os.path.exists(self._exe_path):
            self.open_exe()
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.context_menu.showAt(event.globalPos())
        super().contextMenuEvent(event)