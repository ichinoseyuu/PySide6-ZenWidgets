import sys
import logging
import win32api
import win32con
import win32gui
from ctypes import POINTER, byref, c_bool, c_int, pointer, sizeof, WinDLL, windll, c_long,c_void_p
from ctypes.wintypes import DWORD, LONG, LPCVOID, HRGN, UINT
from PySide6.QtGui import QColor
from .c_structures import (
    ACCENT_STATE,
    DWMNCRENDERINGPOLICY,
    WINDOWCOMPOSITIONATTRIB,
    DWMWINDOWATTRIBUTE,
    DWM_WINDOW_CORNER_PREFERENCE,
    MARGINS,ACCENT_POLICY,
    WINDOWCOMPOSITIONATTRIBDATA,
    DWM_BLURBEHIND
    )
from ctypes import POINTER, c_int, WINFUNCTYPE
from ctypes.wintypes import DWORD, HWND, RECT, BOOL
from .win32_func import isGreaterEqualWin10, isGreaterEqualWin11, isCompositionEnabled

class WindowsWindowEffect:
    """ windows窗口特效类 """

    def __init__(self, window):
        self.window = window

        # 声明 Windows API 函数签名
        self.user32 = WinDLL("user32")
        self.dwmapi = WinDLL("dwmapi")
        self.SetWindowCompositionAttribute = self.user32.SetWindowCompositionAttribute
        self.DwmExtendFrameIntoClientArea = self.dwmapi.DwmExtendFrameIntoClientArea
        self.DwmEnableBlurBehindWindow = self.dwmapi.DwmEnableBlurBehindWindow
        self.DwmSetWindowAttribute = self.dwmapi.DwmSetWindowAttribute

        self.RedrawWindow = self.user32.RedrawWindow
        self.RedrawWindow.argtypes = [c_int, HRGN, HRGN, UINT]
        self.RedrawWindow.restype = BOOL

        # 设置函数返回值类型
        self.SetWindowCompositionAttribute.restype = c_bool
        self.DwmExtendFrameIntoClientArea.restype = LONG
        self.DwmEnableBlurBehindWindow.restype = LONG
        self.DwmSetWindowAttribute.restype = LONG

        # 设置函数参数类型
        self.SetWindowCompositionAttribute.argtypes = [
            c_int,
            POINTER(WINDOWCOMPOSITIONATTRIBDATA),
        ]
        self.DwmSetWindowAttribute.argtypes = [c_int, DWORD, LPCVOID, DWORD]
        self.DwmExtendFrameIntoClientArea.argtypes = [c_int, POINTER(MARGINS)]
        self.DwmEnableBlurBehindWindow.argtypes = [c_int, POINTER(DWM_BLURBEHIND)]

        # 初始化结构体
        self.accentPolicy = ACCENT_POLICY()
        self.winCompAttrData = WINDOWCOMPOSITIONATTRIBDATA()
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        self.winCompAttrData.SizeOfData = sizeof(self.accentPolicy)
        self.winCompAttrData.Data = pointer(self.accentPolicy)

    def setBackgroundColor(self, hWnd, color: QColor):
        """设置窗口背景颜色"""
        hWnd = int(hWnd)
        colorref = DWORD((color.blue() << 16) | (color.green() << 8) | color.red())
        if isGreaterEqualWin11():
            self.DwmSetWindowAttribute(hWnd,
                                    DWMWINDOWATTRIBUTE.DWMWA_CAPTION_COLOR.value,
                                    byref(colorref),
                                    4)
            return

        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_GRADIENT.value
        self.accentPolicy.GradientColor = colorref
        self.accentPolicy.AccentFlags = DWORD(0)
        self.accentPolicy.AnimationId = DWORD(0)
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))


    def RepaintWindow(self, hWnd):
        """触发窗口重绘"""
        hWnd = int(hWnd)
        # 参数说明：
        # 1. 窗口句柄
        # 2. 重绘区域（None 表示整个窗口）
        # 3. 裁剪区域（None 表示无裁剪）
        # 4. 重绘标志（RDW_INVALIDATE 标记区域为无效，RDW_UPDATENOW 立即重绘）
        self.RedrawWindow(hWnd, None, None, 0x0001 | 0x0100)  # RDW_INVALIDATE | RDW_UPDATENOW

    def removeBackgroundColor(self, hWnd):
        """移除窗口背景颜色"""
        hWnd = int(hWnd)
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_GRADIENT.value
        self.accentPolicy.GradientColor = DWORD(0)
        self.accentPolicy.AccentFlags = DWORD(0)
        self.accentPolicy.AnimationId = DWORD(0)
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))

    def setAcrylicEffect(self, hWnd, gradientColor="F2F2F299", enableShadow=True, animationId=0):
        """为窗口添加亚克力效果(Win10+)

        Args:
            hWnd: 窗口句柄
            gradientColor: 十六进制亚克力混合颜色，对应RGBA四个通道
            enableShadow: 是否启用窗口阴影
            animationId: 启用磨砂动画
        """
        if not isGreaterEqualWin10():
            logging.warning("The acrylic effect is only available on Win10+")
            return

        hWnd = int(hWnd)
        gradientColor = ''.join(gradientColor[i:i+2] for i in range(6, -1, -2))
        gradientColor = DWORD(int(gradientColor, base=16))
        animationId = DWORD(animationId)
        accentFlags = DWORD(0x20 | 0x40 | 0x80 | 0x100) if enableShadow else DWORD(0)
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND.value
        self.accentPolicy.GradientColor = gradientColor
        self.accentPolicy.AccentFlags = accentFlags
        self.accentPolicy.AnimationId = animationId
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))

    def setCornerPreference(self, hWnd, preference: DWM_WINDOW_CORNER_PREFERENCE):
        """设置窗口圆角偏好"""
        hWnd = int(hWnd)
        corner_preference = c_int(preference.value)
        self.DwmSetWindowAttribute(hWnd,
                                   DWMWINDOWATTRIBUTE.DWMWA_WINDOW_CORNER_PREFERENCE.value,
                                   byref(corner_preference),
                                   4)

    def setBorderAccentColor(self, hWnd, color: QColor):
        """ 设置窗口边框颜色(win11)

        Args:
            hWnd: 窗口句柄
            color: 边框颜色
        """
        if not isGreaterEqualWin11():
            return

        hWnd = int(hWnd)
        colorref =  DWORD(color.red() | (color.green() << 8) | (color.blue() << 16))
        self.DwmSetWindowAttribute(hWnd,
                                   DWMWINDOWATTRIBUTE.DWMWA_BORDER_COLOR.value,
                                   byref(colorref),
                                   4)

    def removeBorderAccentColor(self, hWnd):
        """ 移除窗口边框颜色(win11)

        Args:
            hWnd: 窗口句柄
        """
        if not isGreaterEqualWin11():
            return

        hWnd = int(hWnd)
        self.DwmSetWindowAttribute(hWnd,
                                   DWMWINDOWATTRIBUTE.DWMWA_BORDER_COLOR.value,
                                   byref(DWORD(0xFFFFFFFF)),
                                   4)

    def setMicaEffect(self, hWnd, isDarkMode=False, isAlt=False):
        """为窗口添加 Mica 效果(Win11)

        Args:
            hWnd: 窗口句柄
            isDarkMode: 是否使用深色模式
            isAlt: 是否启用 Mica Alt 效果
        """
        if not isGreaterEqualWin11():
            logging.warning("The mica effect is only available on Win11")
            return

        hWnd = int(hWnd)
        # fix issue #125
        margins = MARGINS(16777215, 16777215, 0, 0)
        self.DwmExtendFrameIntoClientArea(hWnd, byref(margins))

        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_HOSTBACKDROP.value
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))

        if isDarkMode:
            self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_USEDARKMODECOLORS.value
            self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))

        if sys.getwindowsversion().build < 22523:
            self.DwmSetWindowAttribute(hWnd, 1029, byref(c_int(1)), 4)
        else:
            self.DwmSetWindowAttribute(hWnd, DWMWINDOWATTRIBUTE.DWMWA_SYSTEMBACKDROP_TYPE.value, byref(c_int(4 if isAlt else 2)), 4)

        self.DwmSetWindowAttribute(hWnd, DWMWINDOWATTRIBUTE.DWMWA_USE_IMMERSIVE_DARK_MODE.value, byref(c_int(1*isDarkMode)), 4)

    def setAeroEffect(self, hWnd):
        """为窗口添加 Aero 效果(win7+)

        Args:
            hWnd: 窗口句柄
        """
        hWnd = int(hWnd)
        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_BLURBEHIND.value
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))

    def removeBackgroundEffect(self, hWnd):
        """移除窗口背景效果

        Args:
            hWnd: 窗口句柄
        """
        hWnd = int(hWnd)
        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_DISABLED.value
        self.SetWindowCompositionAttribute(hWnd, pointer(self.winCompAttrData))


    def addShadowEffect(self, hWnd):
        """为窗口添加 DWM 阴影

        Args:
            hWnd: 窗口句柄
        """
        if not isCompositionEnabled():
            return
        # 转换窗口句柄为整数
        hWnd = int(hWnd)
        # 扩展阴影区域
        margins = MARGINS(-1, -1, -1, -1)
        self.DwmExtendFrameIntoClientArea(hWnd, byref(margins))

    def addClassicShadow(self, hWnd):
        """为窗口添加经典阴影效果

        Args:
            hWnd: 窗口句柄
        """
        # 检查系统架构
        is_64bits = sizeof(c_int) == sizeof(c_long)

        # 获取当前窗口类样式
        if is_64bits:
            class_style = win32gui.GetClassLong(hWnd, win32con.GCL_STYLE)
            # 使用 SetClassLongPtr
            windll.user32.SetClassLongPtrW(
                hWnd,
                win32con.GCL_STYLE,
                class_style | 0x00020000
            )
        else:
            # 32位系统使用 SetClassLong
            class_style = win32gui.GetClassLong(hWnd, win32con.GCL_STYLE)
            win32gui.SetClassLong(
                hWnd,
                win32con.GCL_STYLE,
                class_style | 0x00020000
            )

    def addMenuShadowEffect(self, hWnd):
        """为菜单添加 DWM 阴影

        Args:
            hWnd: 窗口句柄
        """
        if not isCompositionEnabled():
            return

        hWnd = int(hWnd)
        self.DwmSetWindowAttribute(
            hWnd,
            DWMWINDOWATTRIBUTE.DWMWA_NCRENDERING_POLICY.value,
            byref(c_int(DWMNCRENDERINGPOLICY.DWMNCRP_ENABLED.value)),
            4,
        )
        margins = MARGINS(-1, -1, -1, -1)
        self.DwmExtendFrameIntoClientArea(hWnd, byref(margins))

    def removeShadowEffect(self, hWnd):
        """移除窗口的 DWM 阴影

        Args:
            hWnd: 窗口句柄
        """
        hWnd = int(hWnd)
        self.DwmSetWindowAttribute(
            hWnd,
            DWMWINDOWATTRIBUTE.DWMWA_NCRENDERING_POLICY.value,
            byref(c_int(DWMNCRENDERINGPOLICY.DWMNCRP_DISABLED.value)),
            4,
        )

    @staticmethod
    def removeMenuShadowEffect(hWnd):
        """移除弹出菜单的阴影效果

        Args:
            hWnd: 窗口句柄
        """
        hWnd = int(hWnd)
        style = win32gui.GetClassLong(hWnd, win32con.GCL_STYLE)
        style &= ~0x00020000  # CS_DROPSHADOW
        win32api.SetClassLong(hWnd, win32con.GCL_STYLE, style)

    @staticmethod
    def addWindowAnimation(hWnd):
        """启用窗口的最大化和最小化动画效果

        Args:
            hWnd: 窗口句柄
        """
        hWnd = int(hWnd)
        style = win32gui.GetWindowLong(hWnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(
            hWnd,
            win32con.GWL_STYLE,
            style
            | win32con.WS_MINIMIZEBOX
            | win32con.WS_MAXIMIZEBOX
            | win32con.WS_CAPTION
            | win32con.CS_DBLCLKS
            | win32con.WS_THICKFRAME,
        )

    @staticmethod
    def disableMaximizeButton(hWnd):
        """禁用窗口的最大化按钮

        Args:
            hWnd: 窗口句柄
        """
        hWnd = int(hWnd)
        style = win32gui.GetWindowLong(hWnd, win32con.GWL_STYLE)
        win32gui.SetWindowLong(
            hWnd,
            win32con.GWL_STYLE,
            style & ~win32con.WS_MAXIMIZEBOX,
        )

    def enableBlurBehindWindow(self, hWnd):
        """启用整个客户区域后的模糊效果

        Args:
            hWnd: 窗口句柄
        """
        blurBehind = DWM_BLURBEHIND(1, True, 0, False)
        self.DwmEnableBlurBehindWindow(int(hWnd), byref(blurBehind))