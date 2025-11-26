from enum import Enum
from dataclasses import dataclass,fields,is_dataclass
import logging
from typing import TypeVar,Dict
from PySide6.QtGui import QColor
from ZenWidgets.core import SingletonMeta,NonInstantiableMeta,ColorConverter
from ZenWidgets.gui.theme import ZThemeManager

__all__ = [
    'ZPaletteKey',
    'ZColorDataKey',
    'ZPalette',
    'ZStyleDataManager',
    'ZFramelessWindowColorData',
    'ZTitleBarButtonColorData',
    'ZToolTipColorData',
    'ZPanelColorData',
    'ZScrollPanelColorData',
    'ZCardColorData',
    'ZButtonColorData',
    'ZRepeatButtonColorData',
    'ZLongPressButtonColorData',
    'ZProgressButtonColorData',
    'ZSwitchColorData',
    'ZComboBoxColorData',
    'ZComboBoxViewColorData',
    'ZComboBoxItemColorData',
    'ZToggleButtonColorData',
    'ZSliderColorData',
    'ZLineEditColorData',
    'ZLoginEditColorData',
    'ZNumberEditColorData',
    'ZHeadLineColorData',
    'ZTextBlockColorData',
    'ZDialogColorData',
    'ZNavigationBarColorData',
    'ZNavBarButtonColorData',
    'ZNavBarToggleButtonColorData',
    'ColorDataT'
]

# region ZPaletteKey
class ZPaletteKey(Enum):
    WindowBackground = 'WindowBackground'
    PanelBody = 'PanelBody'
    CardBody = 'CardBody'
    SwitchHandle = 'SwitchHandle'
    SliderHandle = 'SliderHandle'
    ScrollHandle = 'ScrollHandle'
    Underline = 'Underline'
    BodyDarker = 'BodyDarker'
    Body = 'Body'
    BodyLighter = 'BodyLighter'
    BodyNeutral = 'BodyNeutral'
    BorderEmphasized = 'BorderEmphasized'
    Border ='Border'
    BorderMuted = 'BorderMuted'
    BorderNeutral = 'BorderNeutral'
    TextEmphasized = 'TextEmphasized'
    Text = 'Text'
    TextMuted = 'TextMuted'
    TextNeutral = 'TextNeutral'
    IconEmphasized = 'IconEmphasized'
    Icon = 'Icon'
    IconMuted = 'IconMuted'
    IconNeutral = 'IconNeutral'
    Primary = 'Primary'
    Secondary = 'Secondary'
    Accent = 'Accent'
    Info = 'Info'
    Success = 'Success'
    Warning = 'Warning'
    Danger = 'Danger'

# region ZColorDataKey
class ZColorDataKey(Enum):
    Text = 'Text'
    TextBackSectcted = 'TextBackSectcted'
    TextToggled = 'TextToggled'
    Icon = 'Icon'
    IconToggled = 'IconToggled'
    Body = 'Body'
    BodySatrt = 'BodyStart'
    BodyEnd = 'BodyEnd'
    BodyFocused = 'BodyFocused'
    BodyToggled = 'BodyToggled'
    BodyToggledHover = 'BodyToggledHover'
    BodyToggledPressed = 'BodyToggledPressed'
    RegionHeader = 'RegionHeader'
    RegionContent = 'RegionContent'
    RegionFooter = 'RegionFooter'
    Border = 'Border'
    BorderToggled = 'BorderToggled'
    Handle = 'Handle'
    HandleToggled = 'HandleToggled'
    HandleBorder = 'HandleBorder'
    HandleInner = 'HandleInner'
    HandleOuter = 'HandleOuter'
    Track = 'Track'
    TrackBorder = 'TrackBorder'
    FillArea = 'FillArea'
    FillAreaStart = 'FillAreaStart'
    FillAreaEnd = 'FillAreaEnd'
    FillAreaBorder = 'FillAreaBorder'
    Underline = 'Underline'
    UnderlineFocused = 'UnderlineFocused'
    Cursor = 'Cursor'
    Mask = 'Mask'
    Indicator = 'Indicator'
    PlaceHolder = 'PlaceHolder'
    Shadow = 'Shadow'
    Progress = 'Progress'

# region light_palette
light_palette = {
    ZPaletteKey.WindowBackground: '#F2F2F2',
    ZPaletteKey.PanelBody: '#FFFFFF',
    ZPaletteKey.CardBody: '#FDFDFD',
    ZPaletteKey.SwitchHandle: '#BFBFBF',
    ZPaletteKey.SliderHandle: '#FFFFFF',
    ZPaletteKey.ScrollHandle: '#CFCFCF',
    ZPaletteKey.Underline: '#DFDFDF',
    ZPaletteKey.BodyDarker: '#F6F6F6',
    ZPaletteKey.Body: '#F9F9F9',
    ZPaletteKey.BodyLighter: '#FCFCFC',
    ZPaletteKey.BodyNeutral: '#BFBFBF',
    ZPaletteKey.BorderEmphasized: '#DBDBDB',
    ZPaletteKey.Border: '#E0E0E0',
    ZPaletteKey.BorderMuted: '#EBEBEB',
    ZPaletteKey.BorderNeutral: '#BFBFBF',
    ZPaletteKey.TextEmphasized: '#111111',
    ZPaletteKey.Text: '#333333',
    ZPaletteKey.TextMuted: '#666666',
    ZPaletteKey.TextNeutral: '#9f9f9f',
    ZPaletteKey.IconEmphasized: '#737373',
    ZPaletteKey.Icon: '#737373',
    ZPaletteKey.IconMuted: '#8C8C8C',
    ZPaletteKey.IconNeutral: '#8C8C8C',
    ZPaletteKey.Primary: '#7FCDFF',
    ZPaletteKey.Secondary: '#B8DFFF',
    ZPaletteKey.Accent: '#FFAFCD',
    ZPaletteKey.Info: '#D5DADD',
    ZPaletteKey.Success: '#C2EBAD',
    ZPaletteKey.Warning: '#EBDBAD',
    ZPaletteKey.Danger: '#F6B1B1'
}

# region dark_palette
dark_palette = {
    ZPaletteKey.WindowBackground: '#101010',
    ZPaletteKey.PanelBody: '#151515',
    ZPaletteKey.CardBody: '#181818',
    ZPaletteKey.SwitchHandle: '#A0A0A0',
    ZPaletteKey.SliderHandle: '#181818',
    ZPaletteKey.ScrollHandle: '#505050',
    ZPaletteKey.Underline: '#242424',
    ZPaletteKey.BodyDarker: '#171717',
    ZPaletteKey.Body: '#1C1C1C',
    ZPaletteKey.BodyLighter: '#212121',
    ZPaletteKey.BodyNeutral: '#909090',
    ZPaletteKey.BorderEmphasized: '#323232',
    ZPaletteKey.Border: '#272727',
    ZPaletteKey.BorderMuted: '#242424',
    ZPaletteKey.BorderNeutral: '#505050',
    ZPaletteKey.TextEmphasized: '#EFEFEF',
    ZPaletteKey.Text: '#D9D9D9',
    ZPaletteKey.TextMuted: '#B3B3B3',
    ZPaletteKey.TextNeutral: '#9F9F9F',
    ZPaletteKey.IconEmphasized: '#CCCCCC',
    ZPaletteKey.Icon: '#CCCCCC',
    ZPaletteKey.IconMuted: '#B3B3B3',
    ZPaletteKey.IconNeutral: '#B3B3B3',
    ZPaletteKey.Primary: "#785496",
    ZPaletteKey.Secondary: "#9A6FBD",
    ZPaletteKey.Accent: '#FE9ADD',
    ZPaletteKey.Info: '#75738C',
    ZPaletteKey.Success: '#7FB464',
    ZPaletteKey.Warning: '#C6A953',
    ZPaletteKey.Danger: '#D16161'
}

# region ZPalette
class ZPalette(metaclass=NonInstantiableMeta):
    """全局唯一的调色板"""
    WindowBackground: QColor
    PanelBody: QColor
    CardBody: QColor
    SwitchHandle: QColor
    SliderHandle: QColor
    ScrollHandle: QColor
    Underline: QColor
    BodyDarker: QColor
    Body: QColor
    BodyLighter: QColor
    BodyNeutral: QColor
    BorderEmphasized: QColor
    Border: QColor
    BorderMuted: QColor
    BorderNeutral: QColor
    TextEmphasized: QColor
    Text: QColor
    TextMuted: QColor
    TextNeutral: QColor
    IconEmphasized: QColor
    Icon: QColor
    IconMuted: QColor
    IconNeutral: QColor
    Primary: QColor
    Secondary: QColor
    Accent: QColor
    Info: QColor
    Success: QColor
    Warning: QColor
    Danger: QColor

    Transparent_000 = QColor('#00000000')
    '''- #00000000'''
    Transparent_FFF = QColor('#00FFFFFF')
    '''- #00FFFFFF'''
    Black = QColor('#000000')
    '''- #000000'''
    Black_11 = QColor('#1B1B1B')
    '''- #1B1B1B'''
    Black_19 = QColor('#303030')
    '''- #303030'''
    Black_28 = QColor('#474747')
    '''- #474747'''
    Black_37 = QColor('#5E5E5E')
    '''- #5E5E5E'''
    Black_47 = QColor('#777777')
    '''- #777777'''
    Black_57 = QColor('#919191')
    '''- #919191'''
    Black_67 = QColor('#ABABAB')
    '''- #ABABAB'''
    Black_78 = QColor('#C6C6C6')
    '''- #C6C6C6'''
    Black_89 = QColor('#E2E2E2')
    '''- #E2E2E2'''
    Black_95 = QColor('#F1F1F1')
    '''- #F1F1F1'''
    White = QColor('#FFFFFF')
    '''- #FFFFFF'''

    @classmethod
    def Transparent(cls) -> QColor:
        """
        根据主题自动选择透明色
        - LightTheme: '#00FFFFFF'
        - DarkTheme: '#00000000'
        """
        return cls.Transparent_FFF if ZThemeManager().isLightTheme() else cls.Transparent_000

    @classmethod
    def Transparent_reverse(cls) -> QColor:
        """
        根据主题自动选择与主题反色的透明色
        - LightTheme: '#00000000'
        - DarkTheme: '#00FFFFFF'
        """
        return cls.Transparent_000 if ZThemeManager().isLightTheme() else cls.Transparent_FFF
    @classmethod
    def loadFromDict(cls, palette_dict: Dict[ZPaletteKey, str]) -> None:
        """
        从字典加载调色板配置并更新成员变量

        :param palette_dict: 键为ZPaletteKey枚举，值为颜色字符串的字典
        """
        # 获取所有字段名映射（用于校验）
        field_names = cls.__annotations__.keys()

        for key, color_str in palette_dict.items():
            # 检查键是否有效
            if not isinstance(key, ZPaletteKey):
                raise ValueError(f"无效的调色板键类型: {type(key)}, 应为ZPaletteKey")
            # 检查是否存在对应的成员变量
            if key.value not in field_names:
                raise ValueError(f"调色板中不存在键: {key.value}")
            # 转换颜色并赋值
            setattr(cls, key.value, QColor(color_str))

    @classmethod
    def loadLightPalette(cls) -> None:
        """
        加载内置浅色调色板
        """
        cls.loadFromDict(light_palette)

    @classmethod
    def loadDarkPalette(cls) -> None:
        """
        加载内置深色调色板
        """
        cls.loadFromDict(dark_palette)

# region style_data_map
style_data_map={
    'Light': {
        'ZFramelessWindow': {
            ZColorDataKey.Body: lambda: ZPalette.WindowBackground
        },
        'ZTitleBarButton': {
            ZColorDataKey.Icon: '#333333'
        },
        'ZToolTip': {
            ZColorDataKey.Body: lambda: ZPalette.PanelBody,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text
        },
        ('ZPanel','ZScrollPanel','ZComboBoxView'): {
            ZColorDataKey.Body: lambda: ZPalette.PanelBody,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Handle: lambda: ZPalette.ScrollHandle,
            ZColorDataKey.HandleBorder: lambda: ZPalette.ScrollHandle
        },
        'ZCard': {
            ZColorDataKey.Body: lambda: ZPalette.CardBody,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Underline: lambda: ZPalette.Underline
        },
        ('ZButton','ZRepeatButton','ZComboBox','ZComboBoxItem'): {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.Indicator: lambda: ZPalette.Primary
        },
        'ZLongPressButton': {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.Indicator: lambda: ZPalette.Primary,
            ZColorDataKey.Progress: lambda: ZPalette.Danger,
        },
        'ZProgressButton': {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.Indicator: lambda: ZPalette.Primary,
            ZColorDataKey.Progress: lambda: ZPalette.Success,
        },
        'ZToggleButton': {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.BodyToggled: lambda: ZPalette.Primary,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.TextToggled: lambda: ZPalette.Text,
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.IconToggled: lambda: ZPalette.Icon
        },
        'ZSwitch':{
            ZColorDataKey.Body: lambda: ZPalette.Primary,
            ZColorDataKey.Border: lambda: ZPalette.BorderNeutral,
            ZColorDataKey.Handle: lambda: ZPalette.SwitchHandle,
            ZColorDataKey.HandleToggled: ZPalette.White
        },
        'ZSlider': {
            ZColorDataKey.Track: lambda: ZPalette.BodyDarker,
            ZColorDataKey.TrackBorder: lambda: ZPalette.Border,
            ZColorDataKey.FillAreaStart: lambda: ZPalette.Primary,
            ZColorDataKey.FillAreaEnd: lambda: ZPalette.Secondary,
            ZColorDataKey.FillAreaBorder: lambda: ZPalette.Primary,
            ZColorDataKey.HandleInner: lambda: ZPalette.Secondary,
            ZColorDataKey.HandleOuter:lambda: ZPalette.SliderHandle,
            ZColorDataKey.HandleBorder: lambda: ZPalette.BorderEmphasized
        },
        ('ZLineEdit','ZLoginEdit','ZNumberEdit'): {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.BodyFocused: lambda: ZPalette.PanelBody,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.PlaceHolder: lambda: ZPalette.TextMuted,
            ZColorDataKey.TextBackSectcted: lambda: ZPalette.Secondary,
            ZColorDataKey.Cursor: lambda: ZPalette.Primary,
            ZColorDataKey.Underline: lambda: ZPalette.Underline,
            ZColorDataKey.UnderlineFocused: lambda: ZPalette.Primary
        },
        ('ZHeadLine','ZTextBlock'):{
            ZColorDataKey.Body: ZPalette.Transparent_000,
            ZColorDataKey.Border: ZPalette.Transparent_000,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.TextBackSectcted: lambda: ZPalette.Primary,
            ZColorDataKey.Indicator: lambda: ZPalette.Primary
        },
        'ZDialog': {
            ZColorDataKey.Body: lambda: ZPalette.PanelBody,
            ZColorDataKey.RegionFooter: lambda: ZPalette.Body,
            ZColorDataKey.Border: lambda: ZPalette.Border,
        },
        'ZNavigationBar': {
            ZColorDataKey.Indicator: lambda: ZPalette.Primary
        },
        'ZNavBarButton': {
            ZColorDataKey.Icon: lambda: ZPalette.Icon
        },
        'ZNavBarToggleButton': {
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.IconToggled: lambda: ZPalette.Primary
        },
    },
    # region -----------------------
    'Dark': {
        'ZFramelessWindow': {
            ZColorDataKey.Body: lambda: ZPalette.WindowBackground
        },
        'ZTitleBarButton': {
            ZColorDataKey.Icon: '#DCDCDC'
        },
        'ZToolTip': {
            ZColorDataKey.Body: lambda: ZPalette.PanelBody,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text
        },
        ('ZPanel','ZScrollPanel','ZComboBoxView'): {
            ZColorDataKey.Body: lambda: ZPalette.PanelBody,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Handle: lambda: ZPalette.ScrollHandle,
            ZColorDataKey.HandleBorder: lambda: ZPalette.ScrollHandle
        },
        'ZCard': {
            ZColorDataKey.Body: lambda: ZPalette.CardBody,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Underline: lambda: ZPalette.Underline
        },
        ('ZButton','ZRepeatButton','ZComboBox','ZComboBoxItem'): {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.Indicator: lambda: ZPalette.Primary
        },
        'ZLongPressButton': {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.Indicator: lambda: ZPalette.Primary,
            ZColorDataKey.Progress: lambda: ZPalette.Danger,
        },
        'ZProgressButton': {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.Indicator: lambda: ZPalette.Primary,
            ZColorDataKey.Progress: lambda: ZPalette.Success,
        },
        'ZToggleButton': {
            ZColorDataKey.Body: lambda: ZPalette.Body,
            ZColorDataKey.BodyToggled: lambda: ZPalette.Primary,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.TextToggled: lambda: ZPalette.Text,
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.IconToggled: lambda: ZPalette.Icon
        },
        'ZSwitch':{
            ZColorDataKey.Body: lambda: ZPalette.Primary,
            ZColorDataKey.Border: lambda: ZPalette.BorderNeutral,
            ZColorDataKey.Handle: lambda: ZPalette.SwitchHandle,
            ZColorDataKey.HandleToggled: ZPalette.Black_78,
        },
        'ZSlider': {
            ZColorDataKey.Track: lambda: ZPalette.BodyLighter,
            ZColorDataKey.TrackBorder: lambda: ZPalette.Border,
            ZColorDataKey.FillAreaStart: lambda: ZPalette.Primary,
            ZColorDataKey.FillAreaEnd: lambda: ZPalette.Secondary,
            ZColorDataKey.FillAreaBorder: lambda: ZPalette.Primary,
            ZColorDataKey.HandleInner: lambda: ZPalette.Secondary,
            ZColorDataKey.HandleOuter:lambda: ZPalette.SliderHandle,
            ZColorDataKey.HandleBorder: lambda: ZPalette.BorderEmphasized
        },
        ('ZLineEdit','ZLoginEdit','ZNumberEdit'): {
            ZColorDataKey.Body: lambda: ZPalette.BodyDarker,
            ZColorDataKey.BodyFocused: lambda: ZPalette.PanelBody,
            ZColorDataKey.Border: lambda: ZPalette.Border,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.PlaceHolder: lambda: ZPalette.TextMuted,
            ZColorDataKey.TextBackSectcted: lambda: ZPalette.Primary,
            ZColorDataKey.Cursor: lambda: ZPalette.Primary,
            ZColorDataKey.Underline: lambda: ZPalette.Underline,
            ZColorDataKey.UnderlineFocused: lambda: ZPalette.Primary
        },
        ('ZHeadLine','ZTextBlock'):{
            ZColorDataKey.Body: ZPalette.Transparent_000,
            ZColorDataKey.Border: ZPalette.Transparent_000,
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.TextBackSectcted: lambda: ZPalette.Primary,
            ZColorDataKey.Indicator: lambda: ZPalette.Primary
        },
        'ZDialog': {
            ZColorDataKey.Body: lambda: ZPalette.PanelBody,
            ZColorDataKey.RegionFooter: lambda: ZPalette.Body,
            ZColorDataKey.Border: lambda: ZPalette.Border,
        },
        'ZNavigationBar': {
            ZColorDataKey.Indicator: lambda: ZPalette.Primary
        },
        'ZNavBarButton': {
            ZColorDataKey.Icon: lambda: ZPalette.Icon
        },
        'ZNavBarToggleButton': {
            ZColorDataKey.Icon: lambda: ZPalette.Icon,
            ZColorDataKey.IconToggled: lambda: ZPalette.Primary
        },
    }
}

@dataclass
class ZColorData: ...

# region Window
@dataclass
class ZFramelessWindowColorData(ZColorData):
    Body: QColor

@dataclass
class ZTitleBarButtonColorData(ZColorData):
    Icon: QColor

# region ToolTip
@dataclass
class ZToolTipColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor

# region Panel
@dataclass
class ZPanelColorData(ZColorData):
    Body: QColor
    Border: QColor

@dataclass
class ZScrollPanelColorData(ZColorData):
    Body: QColor
    Border: QColor
    Handle: QColor
    HandleBorder: QColor

@dataclass
class ZCardColorData(ZColorData):
    Body: QColor
    Border: QColor
    Underline: QColor

# region Button
@dataclass
class ZButtonColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    Icon: QColor

@dataclass
class ZRepeatButtonColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    Icon: QColor

# region ProgressButton
@dataclass
class ZLongPressButtonColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    Icon: QColor
    Progress: QColor

@dataclass
class ZProgressButtonColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    Icon: QColor
    Progress: QColor

# region Switch
@dataclass
class ZSwitchColorData(ZColorData):
    Body: QColor
    Border: QColor
    Handle: QColor
    HandleToggled: QColor

# region ComboBox
@dataclass
class ZComboBoxColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    Icon: QColor

@dataclass
class ZComboBoxViewColorData(ZColorData):
    Body: QColor
    Border: QColor

@dataclass
class ZComboBoxItemColorData(ZColorData):
    Text: QColor
    Icon: QColor
    Indicator: QColor

# region ToggleButton
@dataclass
class ZToggleButtonColorData(ZColorData):
    Body: QColor
    BodyToggled: QColor
    Border: QColor
    Text: QColor
    TextToggled: QColor
    Icon: QColor
    IconToggled: QColor

# region Slider
@dataclass
class ZSliderColorData(ZColorData):
    Track: QColor
    TrackBorder: QColor
    FillAreaStart: QColor
    FillAreaEnd: QColor
    FillAreaBorder: QColor
    HandleInner: QColor
    HandleOuter: QColor
    HandleBorder: QColor

# region LineEdit
@dataclass
class ZLineEditColorData(ZColorData):
    Body: QColor
    BodyFocused: QColor
    Border: QColor
    Text: QColor
    PlaceHolder: QColor
    TextBackSectcted: QColor
    Cursor: QColor
    Underline: QColor
    UnderlineFocused: QColor

@dataclass
class ZLoginEditColorData(ZColorData):
    Body: QColor
    BodyFocused: QColor
    Border: QColor
    Text: QColor
    TextBackSectcted: QColor
    Cursor: QColor
    Underline: QColor
    UnderlineFocused: QColor

@dataclass
class ZNumberEditColorData(ZColorData):
    Body: QColor
    BodyFocused: QColor
    Border: QColor
    Text: QColor
    TextBackSectcted: QColor
    Cursor: QColor
    Underline: QColor
    UnderlineFocused: QColor

# region HeadLine
@dataclass
class ZHeadLineColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    TextBackSectcted: QColor
    Indicator: QColor

@dataclass
class ZTextBlockColorData(ZColorData):
    Body: QColor
    Border: QColor
    Text: QColor
    TextBackSectcted: QColor

# region ZDialog
@dataclass
class ZDialogColorData(ZColorData):
    Body: QColor
    RegionFooter: QColor
    Border: QColor

# region NavigationBar
@dataclass
class ZNavigationBarColorData(ZColorData):
    Indicator: QColor

@dataclass
class ZNavBarButtonColorData(ZColorData):
    Icon: QColor

@dataclass
class ZNavBarToggleButtonColorData(ZColorData):
    Icon: QColor
    IconToggled: QColor

ColorDataT = TypeVar('ColorDataT', bound=ZColorData)

# region ZStyleDataFactory
class ZStyleDataFactory:
    dataclass_map = {
        'ZFramelessWindow': ZFramelessWindowColorData,
        'ZTitleBarButton': ZTitleBarButtonColorData,
        'ZToolTip': ZToolTipColorData,
        'ZPanel': ZPanelColorData,
        'ZScrollPanel': ZScrollPanelColorData,
        'ZCard': ZCardColorData,
        'ZButton': ZButtonColorData,
        'ZRepeatButton': ZRepeatButtonColorData,
        'ZLongPressButton': ZLongPressButtonColorData,
        'ZProgressButton': ZProgressButtonColorData,
        'ZSwitch': ZSwitchColorData,
        'ZComboBox': ZComboBoxColorData,
        'ZComboBoxView': ZComboBoxViewColorData,
        'ZComboBoxItem': ZComboBoxItemColorData,
        'ZToggleButton': ZToggleButtonColorData,
        'ZSlider': ZSliderColorData,
        'ZLineEdit': ZLineEditColorData,
        'ZLoginEdit': ZLoginEditColorData,
        'ZNumberEdit': ZNumberEditColorData,
        'ZHeadLine': ZHeadLineColorData,
        'ZTextBlock': ZTextBlockColorData,
        'ZDialog': ZDialogColorData,
        'ZNavigationBar': ZNavigationBarColorData,
        'ZNavBarButton': ZNavBarButtonColorData,
        'ZNavBarToggleButton': ZNavBarToggleButtonColorData,
    }

    @classmethod
    def create(cls, name: str, map: dict) -> ColorDataT:
        data_type = cls.dataclass_map.get(name)
        if data_type is None: raise ValueError(f"Unknown style data class for component: {name}")
        return cls.dictToDataclass(data_type, name, map)

    @staticmethod
    def dictToDataclass(data_type: ColorDataT, name: str, map: dict) -> ColorDataT:
        if not is_dataclass(data_type): raise TypeError(f"{data_type} is not a dataclass")
        # 获取组件对应的样式数据字典
        component_data = {}
        for key, value in map.items():
            if (isinstance(key, tuple) and name in key) or key == name:
                component_data = value
                break
        if not component_data:
            raise ValueError(f"No style data found for component: {name}")
        # 提取数据类所需的字段
        field_names = [f.name for f in fields(data_type)]
        filtered = {}
        for key, value in component_data.items():
            # 枚举键转换为字符串
            key_str = key.value if isinstance(key, Enum) else str(key)
            if key_str in field_names:
                # 确保值是QColor类型（处理可能的动态颜色值）
                if callable(value):
                    color_value = value()
                    filtered[key_str] = QColor(color_value)
                else:
                    color_value = value
                    filtered[key_str] = QColor(color_value)
        # 检查是否缺失必要字段
        missing = set(field_names) - set(filtered.keys())
        if missing:
            raise ValueError(f"Missing required fields for {data_type.__name__}: {missing}")
        return data_type(**filtered)

# region ZStyleDataManager
class ZStyleDataManager(metaclass=SingletonMeta):
    def __init__(self) -> None:
        super().__init__()
        self._cache: Dict[str, ColorDataT] = {}
        ZThemeManager().themeChanged.connect(self._theme_change_handler_)

    def _take_palette_snapshot(self) -> Dict[str, QColor]:
        """保存当前ZPalette的所有颜色状态"""
        return {
            field: getattr(ZPalette, field)
            for field in ZPalette.__annotations__
            if hasattr(ZPalette, field)
        }

    def _restore_palette_snapshot(self, snapshot: Dict[str, QColor]) -> None:
        """恢复ZPalette到指定的快照状态"""
        for field, color in snapshot.items():
            setattr(ZPalette, field, color)

    def getStyleData(self, name: str) -> ColorDataT:
        '''获取当前主题下的样式数据'''
        # 检查缓存
        if name in self._cache: return self._cache[name]
        # 缓存中没有，则创建并缓存
        style_data = ZStyleDataFactory.create(name, style_data_map[ZThemeManager().getThemeName()])
        self._cache[name] = style_data
        return style_data

    def getStyleDataByTheme(self, name: str, theme: str) -> ColorDataT:
        '''获取指定主题下的样式数据'''
        current_theme = ZThemeManager().getThemeName()
        if theme == current_theme:
            return self.getStyleData(name)

        # 保存当前调色板状态
        current_snapshot = self._take_palette_snapshot()
        try:
            # 临时切换到目标主题的调色板
            if theme == 'Light':
                ZPalette.loadLightPalette()
            elif theme == 'Dark':
                ZPalette.loadDarkPalette()
            # 创建目标主题的样式数据
            return ZStyleDataFactory.create(name, style_data_map[theme])
        finally:
            # 无论是否发生异常，都恢复原始调色板状态
            self._restore_palette_snapshot(current_snapshot)

    def _theme_change_handler_(self, theme: str) -> None:
        self.clearCache()
        if theme == 'Light':
            ZPalette.loadLightPalette()
        elif theme == 'Dark':
            ZPalette.loadDarkPalette()

    def clearCache(self) -> None:
        """清除所有缓存的样式数据实例，用于主题切换等场景"""
        self._cache.clear()


# region 测试
if __name__ == '__main__':
    # 加载默认调色板（浅色调）
    ZPalette.loadLightPalette()
    logging.info("已加载浅色调色板")

    # 获取所有组件名称列表
    component_names = list(ZStyleDataFactory.dataclass_map.keys())

    # 测试每个组件的样式数据
    logging.info("===== 测试浅色调色板样式 =====")
    for name in component_names:
        try:
            style_data = ZStyleDataManager().getStyleData(name)
            logging.info(f"---{name} 样式数据---")
            for field in fields(style_data):
                value = getattr(style_data, field.name)
                # 打印颜色的十六进制表示
                if isinstance(value, QColor):
                    logging.info(f"  |{field.name}: {value.name()}")
                else:
                    logging.info(f"  |{field.name}: {value}")
        except Exception as e:
            logging.info(f"{name} 样式数据获取失败: {str(e)}")

    # 切换到深色调色板
    ZPalette.loadDarkPalette()
    # 清除缓存以重新生成样式数据
    ZStyleDataManager().clearCache()
    logging.info("已加载深色调色板")

    # 测试深色调色板下的样式数据
    logging.info("===== 测试深色调色板样式 =====")
    for name in component_names:
        try:
            style_data = ZStyleDataManager().getStyleData(name)
            logging.info(f"---{name} 样式数据---")
            for field in fields(style_data):
                value = getattr(style_data, field.name)
                if isinstance(value, QColor):
                    logging.info(f"  |{field.name}: {value.name()}")
                else:
                    logging.info(f"  |{field.name}: {value}")
        except Exception as e:
            logging.info(f"{name} 样式数据获取失败: {str(e)}")

    logging.info("所有样式数据测试完成")

    print(ZPalette.Transparent())
