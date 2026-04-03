from typing import List
from pydantic import BaseModel, Field

from trailine_api.common.types import SkyCondition, DataGoMiddleForecastSkyCondition


class WeatherForecastItemSchema(BaseModel):
    date: str = Field(..., description="예보 날짜 (YYYY-MM-DD)")
    min_temperature: float = Field(..., alias="minTemperature", description="최저 기온 (°C)")
    max_temperature: float = Field(..., alias="maxTemperature", description="최고 기온 (°C)")
    precipitation_probability: int = Field(..., alias="precipitationProbability", description="강수 확률 (%)")
    sky_condition: SkyCondition = Field(..., alias="skyCondition", description="하늘 상태")


class WeatherForecastResponseSchema(BaseModel):
    course_id: int = Field(..., alias="courseId", description="코스 식별자")
    forecasts: List[WeatherForecastItemSchema] = Field(..., description="일기예보 리스트")


class MidLandForecastItem(BaseModel):
    rain_probability_am: int = Field(..., description="오전 강수확률 (%)")
    rain_probability_pm: int = Field(..., description="오후 강수확률 (%)")
    sky_condition_am: DataGoMiddleForecastSkyCondition = Field(..., description="오전 날씨 상태")
    sky_condition_pm: DataGoMiddleForecastSkyCondition = Field(..., description="오후 날씨 상태")


class MidLandTemperatureItem(BaseModel):
    min_temperature: int = Field(..., description="최저 기온 (°C)")
    max_temperature: int = Field(..., description="최고 기온 (°C)")
