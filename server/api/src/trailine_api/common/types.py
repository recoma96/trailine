from enum import StrEnum
from typing import List, Dict, Any, TypeAlias


SQLRow: TypeAlias = Dict[str, Any]
SQLRowList: TypeAlias = List[SQLRow]


class SkyCondition(StrEnum):
    CLEAR = "clear"     # 맑음
    CLOUDY = "cloudy"   # 구름많음, 흐림
    RAIN = "rain"       # 비, 소나기, 비/눈
    SNOW = "snow"       # 눈


class DataGoMiddleForecastSkyCondition(StrEnum):
    def __new__(cls, value: str, korean: str = "", sky_condition: SkyCondition = SkyCondition.CLEAR):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.korean = korean
        obj.sky_condition = sky_condition
        return obj

    CLEAR = ("clear", "맑음", SkyCondition.CLEAR)
    MOSTLY_CLOUDY = ("mostly_cloudy", "구름많음", SkyCondition.CLOUDY)
    MOSTLY_CLOUDY_RAIN = ("mostly_cloudy_rain", "구름많고 비", SkyCondition.RAIN)
    MOSTLY_CLOUDY_SNOW = ("mostly_cloudy_snow", "구름많고 눈", SkyCondition.SNOW)
    MOSTLY_CLOUDY_SLEET = ("mostly_cloudy_sleet", "구름많고 비/눈", SkyCondition.RAIN)
    MOSTLY_CLOUDY_SHOWER = ("mostly_cloudy_shower", "구름많고 소나기", SkyCondition.RAIN)
    OVERCAST = ("overcast", "흐림", SkyCondition.CLOUDY)
    OVERCAST_RAIN = ("overcast_rain", "흐리고 비", SkyCondition.RAIN)
    OVERCAST_SNOW = ("overcast_snow", "흐리고 눈", SkyCondition.SNOW)
    OVERCAST_SLEET = ("overcast_sleet", "흐리고 비/눈", SkyCondition.RAIN)
    OVERCAST_SHOWER = ("overcast_shower", "흐리고 소나기", SkyCondition.RAIN)

    @classmethod
    def from_korean(cls, korean: str) -> "DataGoMiddleForecastSkyCondition":
        for member in cls:
            if member.korean == korean:
                return member
        raise ValueError(f"Unknown korean sky condition: {korean}")

    def to_sky_condition(self) -> SkyCondition:
        return self.sky_condition


class CourseLocationType(StrEnum):
    START = "start"
    MIDDLE = "middle"
    END = "end"
