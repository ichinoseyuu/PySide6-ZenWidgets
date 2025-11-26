from enum import Enum, auto
from typing import TypeVar, Protocol
from dataclasses import dataclass

__all__ = [
    'ZStyleData',
    'StyleDataT',
    'ZSwitchStyleData',
    'ZSliderStyleData',
    'ZStyleProtocol',
    'StyleT',
    'ZButtonStyle',
    'ZSwitchStyle',
    'ZSliderStyle',
]


# region StyleData
@dataclass
class ZStyleData: ...

StyleDataT = TypeVar('StyleDataT', bound=ZStyleData)

@dataclass
class ZSwitchStyleData(ZStyleData):
    Height: int
    Width: int
    HandleDiameter: int
    Margin: int

@dataclass
class ZSliderStyleData(ZStyleData):
    TrackWidth: int
    HandleRadius: int

# region Style
class ZStyleProtocol(Protocol):
    @property
    def value(self): ...

    @property
    def name(self): ...

StyleT = TypeVar('StyleT', bound=ZStyleProtocol)

class ZButtonStyle(Enum):
    Default = auto()
    Flat = auto()

class ZSwitchStyle(Enum):
    Compact = ZSwitchStyleData(Height=20, Width=40, HandleDiameter=16, Margin=2)
    Standard = ZSwitchStyleData(Height=24, Width=48, HandleDiameter=18, Margin=3)
    Comfortable = ZSwitchStyleData(Height=28, Width=56, HandleDiameter=22 , Margin=3)

class ZSliderStyle(Enum):
    Default = ZSliderStyleData(TrackWidth=6, HandleRadius=12)
    Thin = ZSliderStyleData(TrackWidth=4, HandleRadius=10)
    Thick = ZSliderStyleData(TrackWidth=8, HandleRadius=12)
