from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from trailine_api.common.types import (
    SkyCondition,
    DatagoMiddleForecastSkyCondition,
    DatagoShortForecastRainCondition,
    DatagoShortForecastSkyCondition,
)


DAY_OF_WEEK_LIST = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
DAY_OF_WEEK_KO_LIST = ["월", "화", "수", "목", "금", "토", "일"]


class WeatherForecastItemSchema(BaseModel):
    date: str = Field(..., description="예보 날짜 (YYYY-MM-DD)")
    day_of_week: str = Field(..., alias="dayOfWeek", description="요일 (영문)")
    day_of_week_ko: str = Field(..., alias="dayOfWeekKo", description="요일 (한국어)")
    min_temperature: float = Field(..., alias="minTemperature", description="최저 기온 (°C)")
    max_temperature: float = Field(..., alias="maxTemperature", description="최고 기온 (°C)")
    precipitation_probability: int = Field(..., alias="precipitationProbability", description="강수 확률 (%)")
    sky_condition: SkyCondition = Field(..., alias="skyCondition", description="하늘 상태")


class WeatherForecastResponseSchema(BaseModel):
    course_id: int = Field(..., alias="courseId", description="코스 식별자")
    forecasts: List[WeatherForecastItemSchema] = Field(..., description="일기예보 리스트")


class ShortForecastItem(BaseModel):
    forecast_date: datetime = Field(..., description="에보 시점")
    rain_probability: int = Field(..., description="강수 확률 (%)")
    rain_condition: DatagoShortForecastRainCondition = Field(..., description="강수 형태")
    rain_amount: float = Field(..., description="시간당 강수량 (mm)")
    humidity: int = Field(..., description="습도 (%)")
    snow_amount: float = Field(..., description="적설량 (cm)")
    sky_condition: DatagoShortForecastSkyCondition = Field(..., description="하늘 상태")
    temperature: int = Field(..., description="기온 (°C)")
    min_temperature: Optional[int] = Field(default=None, description="일 최저기온 (°C) (0600만 있음)")
    max_temperature: Optional[int] = Field(default=None, description="일 최고기온 (°C) (0600만 있음)")


class MidLandForecastItem(BaseModel):
    rain_probability_am: int = Field(..., description="오전 강수확률 (%)")
    rain_probability_pm: int = Field(..., description="오후 강수확률 (%)")
    sky_condition_am: DatagoMiddleForecastSkyCondition = Field(..., description="오전 날씨 상태")
    sky_condition_pm: DatagoMiddleForecastSkyCondition = Field(..., description="오후 날씨 상태")


class MidLandTemperatureItem(BaseModel):
    min_temperature: int = Field(..., description="최저 기온 (°C)")
    max_temperature: int = Field(..., description="최고 기온 (°C)")
