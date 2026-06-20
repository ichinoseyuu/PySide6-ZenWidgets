import os
from enum import Enum
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QPainterPath, QPen
from ZenWidgets.component.base import ZWidget
from ZenWidgets.core import ZDebug

class ZImage(ZWidget):
    class ScaleType(Enum):
        Fit = 0 # 按比例缩放
        Fill = 1  # 填满
        Stretch = 2  # 拉伸
    def __init__(self,
                 parent: QWidget | None = None,
                 image_path: str | None = None,
                 scale_type: ScaleType = ScaleType.Fit,
                 corner_radius: int = 2,
                 opacity: float = 1.0,
                 objectName: str | None = None
                 ):
        super().__init__(parent,
                         objectName=objectName
                         )
        self._image: QPixmap = QPixmap()       # 原始图片
        self._scaled_pixmap: QPixmap = QPixmap()   # 缩放后的图片
        self._opacity = opacity      # 透明度
        self._scale_type =  scale_type # 缩放类型
        self._corner_radius = corner_radius     # 圆角半径
        self.setAttribute(Qt.WA_TranslucentBackground)  # 支持透明
        self.setImage(image_path)


    def setImage(self, image_path: str) -> bool:
        """设置图片
        Args:
            image_path: 图片路径或资源路径
        Returns:
            bool: 是否成功加载图片
        """
        if not image_path: return False
        # 判断是否是资源路径
        if image_path.startswith(':'):
            self._image = QPixmap(image_path)
        else:
            # 文件路径处理
            if not os.path.exists(image_path):
                print(f"图片文件不存在: {image_path}")
                return False
            self._image = QPixmap(image_path)
        if self._image.isNull():
            print(f"图片加载失败: {image_path}")
            return False
        self._updateScaledImage()
        self.update()
        return True

    def setPixmap(self, pixmap: QPixmap) -> bool:
        """直接设置QPixmap对象
        Args:
            pixmap: QPixmap对象
        Returns:
            bool: 是否成功设置
        """
        if pixmap.isNull():
            print("无效的QPixmap对象")
            return False
        self._image = pixmap
        self._updateScaledImage()
        self.update()
        return True

    def setOpacity(self, opacity: float):
        """设置透明度"""
        self._opacity = max(0.0, min(1.0, opacity))
        self.update()

    def setScaleType(self, scale_type: int):
        """设置缩放类型"""
        if self._scale_type != scale_type:
            self._scale_type = scale_type
            self._updateScaledImage()
            self.update()

    def setCornerRadius(self, radius: int):
        """设置圆角半径"""
        if radius != self._corner_radius:
            self._corner_radius = max(0, radius)
            self.update()

    def cornerRadius(self) -> int:
        """获取圆角半径"""
        return self._corner_radius

    def _updateScaledImage(self):
        """更新缩放后的图片"""
        if not self._image or self._image.isNull():
            return

        size = self.size()
        if size.isEmpty():
            return

        # 设置高质量缩放选项
        transform_mode = Qt.SmoothTransformation

        if self._scale_type == self.ScaleType.Stretch:
            # 拉伸填充
            self._scaled_pixmap = self._image.scaled(
                size,
                Qt.IgnoreAspectRatio,
                transform_mode
            )
        else:
            # 计算保持比例的尺寸
            image_size = self._image.size()

            if self._scale_type == self.ScaleType.Fit:
                # 适应窗口
                scaled_size = image_size.scaled(size, Qt.KeepAspectRatio)
            else:  # Fill
                # 填充窗口
                scaled_size = image_size.scaled(size, Qt.KeepAspectRatioByExpanding)

            self._scaled_pixmap = self._image.scaled(
                scaled_size,
                Qt.KeepAspectRatio,
                transform_mode
                )

    def resizeEvent(self, event):
        """处理大小改变事件"""
        super().resizeEvent(event)
        self._updateScaledImage()

    def sizeHint(self):
        """返回图片的原始大小"""
        return self._image.size()

    def paintEvent(self, event):
        """绘制事件"""
        if not self._scaled_pixmap or self._scaled_pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setOpacity(self._opacity)

        # 计算居中绘制的位置
        x = (self.width() - self._scaled_pixmap.width()) // 2
        y = (self.height() - self._scaled_pixmap.height()) // 2
        if self._corner_radius > 0:
            # 创建圆角路径，使用整个组件的大小
            path = QPainterPath()
            path.addRoundedRect(
                0, 0, self.width(), self.height(),  # 使用组件的完整尺寸
                self._corner_radius, self._corner_radius
            )
            # 设置裁剪路径
            painter.setClipPath(path)
        # 直接绘制图片,不需要额外的圆角处理
        painter.drawPixmap(x, y, self._scaled_pixmap)
        if ZDebug.draw_rect: ZDebug.drawRect(painter, self.rect())
        painter.end()
