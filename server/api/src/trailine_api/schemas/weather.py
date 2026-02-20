from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from trailine_api.integrations.weather.schemas import KmaMountainSkyStatus


class SkyStatusType(str, Enum):
    SUNNY = "sunny"           # 맑음
    PARTLY_CLOUDY = "partly_cloudy"  # 구름 조금
    MOSTLY_CLOUDY = "mostly_cloudy"  # 구름 많음
    OVERCAST = "overcast"         # 흐림
    RAINY = "rainy"             # 비
    SNOWY = "snowy"             # 눈

    @staticmethod
    def get_from_kma_mountain(sky_status: KmaMountainSkyStatus):
        return {
            KmaMountainSkyStatus.SUNNY: SkyStatusType.SUNNY,
            KmaMountainSkyStatus.MOSTLY_CLOUDY: SkyStatusType.MOSTLY_CLOUDY,
            KmaMountainSkyStatus.OVERCAST: SkyStatusType.OVERCAST,
            KmaMountainSkyStatus.RAINY: SkyStatusType.RAINY,
            KmaMountainSkyStatus.SNOWY: SkyStatusType.SNOWY,
        }.get(sky_status)


class CurrentWeather(BaseModel):
    now_at: datetime = Field(..., description="요청시각 (현재시각)", serialization_alias="nowAt")
    offset_hours: int = Field(..., description="상대시간 (x시간 후...)", serialization_alias="offsetHours")
    temperature: float = Field(..., description="현재 온도 (섭씨)")
    precip_amount: float = Field(..., description="1시간 강수량", serialization_alias="precipAmount")
    wind_speed: float = Field(..., description="풍속 (m/s)", serialization_alias="windSpeed")
    wind_dir: float = Field(..., description="풍향 (90도, 180도...)", serialization_alias="windDirection")
    snow_depth: int = Field(..., description="적설량", serialization_alias="snowDepth")
    sky_status: SkyStatusType = Field(..., description="하늘 상태", serialization_alias="skyStatus")
    humidity: float = Field(..., description="습도", serialization_alias="humidity")


class CurrentWeatherResponse(BaseModel):
    weathers: List[CurrentWeather] = Field(..., description="날씨 리스트 (현재부터 몇시간 후 까지 정렬)")
