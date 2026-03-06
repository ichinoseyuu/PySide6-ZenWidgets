from enum import Enum
from dataclasses import dataclass,fields,is_dataclass
import logging
from typing import TypeVar,Dict,Optional,Callable,Union,Any
from PySide6.QtGui import QColor
from PySide6.QtCore import QObject, Signal
from ZenWidgets.core import SingletonMeta,NonInstantiableMeta,ColorConverter
from ZenWidgets.gui.theme import ZThemeManager

__all__ = [
    'ZPaletteKey',
    'ZColorDataKey',
    'ZPalette',
    'ZStyleDataManager',
    'colordata_provider',
    'ZColorData',
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

# region Factory
class ZStyleDataFactory:
    """运行时 dataclass 注册 + dataclass 工厂"""

    # 运行时注册表（component_name -> dataclass type）
    _dataclass_registry: Dict[str, type] = {}

    @classmethod
    def register_dataclass(cls, name: str, dataclass_type: type, /, overwrite: bool = False) -> None:
        """注册 dataclass。默认不覆盖已注册项（幂等）。"""
        existing = cls._dataclass_registry.get(name)
        if existing is dataclass_type:
            logging.debug(f"[DataFactory] {name}: already registered, skip.")
            return
        if existing is not None and not overwrite:
            logging.warning(f"[DataFactory] {name}: already registered with {existing.__name__}; use overwrite=True to replace.")
            return
        cls._dataclass_registry[name] = dataclass_type
        #logging.info(f"[DataFactory] registered '{name}' -> {dataclass_type.__name__}")

    @classmethod
    def get_dataclass(cls, name: str):
        """返回已注册 dataclass（或 None）。"""
        return cls._dataclass_registry.get(name)

    @classmethod
    def get_all_registered_names(cls):
        """返回已注册的所有组件名称列表。"""
        return list(cls._dataclass_registry.keys())

    @classmethod
    def mapToInstance(cls, data_type: type, name: str, map_: dict):
        """通用：从 theme/provider map 生成 data_type 的实例（仅支持 ZColorData 子类）。"""
        # 找到针对 name 的映射（支持 tuple key）
        component_data = {}
        for key, value in map_.items():
            if (isinstance(key, tuple) and name in key) or key == name:
                component_data = value
                break
        if not component_data:
            raise ValueError(f"No style data found for component: {name}")

        # 统一使用 ZColorData 的方法获取字段名
        if issubclass(data_type, ZColorData):
            field_names = data_type.get_field_names()
        else:
            raise TypeError(f"mapToInstance: {data_type.__name__} must inherit from ZColorData")

        # 填充并强制 QColor
        filled = {}
        for key, value in component_data.items():
            key_str = key.value if isinstance(key, Enum) else str(key)
            if key_str in field_names:
                v = value() if callable(value) else value
                filled[key_str] = v if isinstance(v, QColor) else QColor(v)

        missing = set(field_names) - set(filled.keys())
        if missing:
            raise ValueError(f"Missing required fields for {data_type.__name__}: {missing}")

        # 构造实例（ZColorData 子类支持 **filled）
        return data_type(**filled)

    @classmethod
    def create(cls, name: str, map_: dict) -> 'ColorDataT':
        """创建指定组件的 dataclass 实例（使用注册表 dataclass）。"""
        data_type = cls.get_dataclass(name)
        if data_type is None:
            raise ValueError(f"Unknown style data class for component: {name}")
        return cls.mapToInstance(data_type, name, map_)

    @classmethod
    def create_from_defaults(cls, name: str) -> 'ColorDataT':
        """基于 dataclass 字段与 ZPalette 的启发式映射生成默认样式数据。"""
        data_type = cls.get_dataclass(name)
        if data_type is None:
            raise ValueError(f"Unknown style data class for component: {name}")

        # 支持 dataclass 或继承自 ZColorData 的自定义类
        if is_dataclass(data_type):
            field_names = [f.name for f in fields(data_type)]
        elif issubclass(data_type, ZColorData):
            field_names = data_type.get_field_names()
        else:
            raise TypeError(f"create_from_defaults: {data_type.__name__} must be a dataclass or inherit from ZColorData")

        filled: Dict[str, QColor] = {}
        for fn in field_names:
            if fn in ZPalette.__annotations__:
                filled[fn] = getattr(ZPalette, fn)
                continue
            lower = fn.lower()
            if 'text' in lower:
                filled[fn] = ZPalette.Text
            elif 'border' in lower:
                filled[fn] = ZPalette.Border
            elif 'indicator' in lower or 'progress' in lower:
                filled[fn] = ZPalette.Primary
            elif 'handle' in lower or 'track' in lower or 'fillarea' in lower or 'underline' in lower:
                filled[fn] = ZPalette.Body
            elif 'cursor' in lower or 'placeholder' in lower:
                filled[fn] = ZPalette.TextMuted
            else:
                filled[fn] = ZPalette.Transparent()
        return data_type(**filled)

class _StyleSignals(QObject):
    """承载 styleChanged 信号 (str: component name or empty for global)."""
    styleChanged = Signal(str)

# region ZStyleDataManager
class ZStyleDataManager(metaclass=SingletonMeta):
    def __init__(self) -> None:
        super().__init__()
        self._cache: Dict[str, ColorDataT] = {}
        # name -> provider (callable(theme)->mapping) | dict | mapping
        self._providers: Dict[str, Union[Callable[[str], dict], dict, None]] = {}
        # 信号承载对象
        self._signals = _StyleSignals()
        # 公开信号用于外部订阅： sd_mgr = ZStyleDataManager(); sd_mgr.styleChanged.connect(...)
        self.styleChanged = self._signals.styleChanged
        ZThemeManager().themeChanged.connect(self._theme_change_handler_)

    def notifyStyleChanged(self, name: Optional[str] = None) -> None:
        """触发 styleChanged(name)；name 为 '' 表示全局通知。"""
        self._signals.styleChanged.emit(name or '')

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

    def getStyleData(self, name: str) -> 'ColorDataT':
        """获取当前主题下的样式数据（优先 provider -> fallback defaults）。"""
        if name in self._cache:
            return self._cache[name]

        theme = ZThemeManager().getThemeName()
        provider = self._providers.get(name)

        # 优先使用 provider（callable | dict per-theme | plain mapping）
        if provider is not None:
            try:
                if callable(provider):
                    component_map = provider(theme)
                elif isinstance(provider, dict) and theme in provider:
                    component_map = provider[theme]
                else:
                    component_map = provider
                # 使用 mapToInstance，要求 dataclass/class 已通过 colordata_class 注册
                data_type = ZStyleDataFactory.get_dataclass(name)
                if data_type is None:
                    logging.debug(f"Provider present for '{name}' but no dataclass registered; fallback to defaults.")
                    style_data = ZStyleDataFactory.create_from_defaults(name)
                else:
                    style_data = ZStyleDataFactory.mapToInstance(data_type, name, {name: component_map})
            except Exception:
                logging.exception(f"Provider for '{name}' failed, falling back to defaults.")
                style_data = ZStyleDataFactory.create_from_defaults(name)
        else:
            logging.debug(f"No provider for '{name}', falling back to defaults.")
            style_data = ZStyleDataFactory.create_from_defaults(name)

        self._cache[name] = style_data
        return style_data

    def registerStyleProvider(self, name: str, provider: Optional[Union[Callable[[str], dict], dict, Any]]=None, /, update: bool = False) -> None:
        """注册 provider（callable/theme->map/直接 map）。update=True 可触发 styleChanged 通知。"""
        existing = self._providers.get(name, None)
        # 快速判断是否相同：相同对象或 dict 值相等
        same = False
        if existing is provider:
            same = True
        elif isinstance(existing, dict) and isinstance(provider, dict) and existing == provider:
            same = True
        if same:
            logging.debug(f"[StyleMgr] {name}: unchanged, skip.")
            return

        #logging.info(f"[StyleMgr] register provider: {name}.")
        self._providers[name] = provider
        self.clearCache()
        if update:
            #logging.info(f"[StyleMgr] update for '{name}'.")
            self.notifyStyleChanged(name)

    def unregisterStyleProvider(self, name: str) -> None:
        self._providers.pop(name, None)
        self.clearCache()
        logging.info(f"[StyleMgr] unregister provider: {name}.")
        self.notifyStyleChanged(name)

    def getStyleDataByTheme(self, name: str, theme: str) -> 'ColorDataT':
        """获取指定主题下的样式数据（在临时切换调色板的上下文中评估 provider 或 defaults）。"""
        current_theme = ZThemeManager().getThemeName()
        if theme == current_theme:
            return self.getStyleData(name)

        current_snapshot = self._take_palette_snapshot()
        try:
            if theme == 'Light':
                ZPalette.loadLightPalette()
            elif theme == 'Dark':
                ZPalette.loadDarkPalette()

            provider = self._providers.get(name)
            if provider is not None:
                try:
                    if callable(provider):
                        component_map = provider(theme)
                    elif isinstance(provider, dict) and theme in provider:
                        component_map = provider[theme]
                    else:
                        component_map = provider
                    data_type = ZStyleDataFactory.get_dataclass(name)
                    if data_type is None:
                        logging.debug(f"[StyleMgr] {name}: unfind, fallback to defaults.")
                        return ZStyleDataFactory.create_from_defaults(name)
                    return ZStyleDataFactory.mapToInstance(data_type, name, {name: component_map})
                except Exception:
                    logging.exception(f"[StyleMgr] {name}: provider failed, fallback to defaults.")
                    return ZStyleDataFactory.create_from_defaults(name)
            else:
                logging.debug(f"[StyleMgr] {name}: no provider, fallback to defaults.")
                return ZStyleDataFactory.create_from_defaults(name)
        finally:
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

# region colordata_provider
def colordata_provider(name: Optional[str] = None, datamap: Optional[Union[Callable[[str], dict], dict]] = None, classtype: Optional[type] = None):
    """
    装饰器：在控件定义处注册 provider
    默认在内部调用 registerStyleProvider(..., update=True) 以触发热更新通知。
    """
    def deco(cls):
        comp = name or cls.__name__
        # 若提供 dataclass，确保先注册 dataclass
        if classtype:
            ZStyleDataFactory.register_dataclass(comp, classtype)
        sd_mgr = ZStyleDataManager()
        existing_provider = sd_mgr._providers.get(comp, None)
        provider_same = False
        if existing_provider is datamap:
            provider_same = True
        elif isinstance(existing_provider, dict) and isinstance(datamap, dict) and existing_provider == datamap:
            provider_same = True

        if provider_same:
            logging.debug(f"style_provider: provider for '{comp}' unchanged, skip register.")
        else:
            # 使用 update=True 触发通知，确保热更新链路可工作
            sd_mgr.registerStyleProvider(comp, datamap, update=True)
            #logging.info(f"style_provider: provider for '{comp}' registered.")
        return cls
    return deco

# region ZColorData
class ZColorData:
    """
    - 支持两种字段声明方式：
      1) 类注解： class MyData(ZColorData): Text: QColor; Body: QColor
      2) 自定义 __fields__ 列表： __fields__ = ['Text','Body']
    - 构造接受 kwargs 并做字段校验，用法和 dataclass 一致
    """
    __fields__: Optional[list] = None

    def __init__(self, /, **kwargs):
        # 获取字段名（优先 __fields__，否则用 __annotations__）
        field_names = self.get_field_names()
        missing = set(field_names) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required fields for {self.__class__.__name__}: {missing}")
        for k in field_names:
            v = kwargs[k]
            setattr(self, k, v)

    @classmethod
    def get_field_names(cls) -> list:
        if cls.__fields__:
            return list(cls.__fields__)
        ann = getattr(cls, '__annotations__', {})
        return sorted(ann.keys())  # 排序保证顺序稳定

    def as_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self.get_field_names()}

    def __repr__(self) -> str:
        """重写repr，输出和dataclass一致的格式"""
        fields = self.get_field_names()
        field_strs = [f"{name}={getattr(self, name)!r}" for name in fields]
        return f"{self.__class__.__name__}({', '.join(field_strs)})"

ColorDataT = TypeVar('ColorDataT', bound=ZColorData)



# region 测试
if __name__ == '__main__':
    # 加载默认调色板（浅色调）
    ZPalette.loadLightPalette()
    print("已加载浅色调色板")
    # -----------------------
    # 装饰器示例：在类定义处自动注册 style provider（MyZWidget）
    # -----------------------
    class MyZWidgetColorData(ZColorData):
        Text: QColor
        Body: QColor

    # 显式 provider（按主题返回 mapping）
    my_provider = {
        'Light': {
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.Body: lambda: ZPalette.Body
        },
        'Dark': {
            ZColorDataKey.Text: lambda: ZPalette.Text,
            ZColorDataKey.Body: lambda: ZPalette.BodyDarker
        }
    }

    @colordata_provider(name='MyZWidget', datamap=my_provider, classtype=MyZWidgetColorData)
    class MyZWidget:
        """示例控件（仅用于测试装饰器注册）"""
        def __init__(self):
            self.data = ZStyleDataManager().getStyleData('MyZWidget')
            self.data1 = MyZWidgetColorData(Text=QColor(255, 0, 0), Body=QColor(0, 255, 0))
        pass

    print("===== 测试实例 =====")
    widget1 = MyZWidget()
    widget2 = MyZWidget()
    print(f"MyZWidget.Text: {widget1.data.Text.name()}, Body: {widget1.data.Body.name()}")
    print(widget1.data)
    print(widget1.data1)
    print(ZStyleDataManager()._cache)
    print(ZStyleDataManager()._providers)
    print(ZStyleDataFactory._dataclass_registry)


