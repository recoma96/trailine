from datetime import datetime
from enum import IntEnum, StrEnum

from pydantic import BaseModel, Field


class KmaMountainSkyStatus(IntEnum):
    SUNNY = 1
    MOSTLY_CLOUDY = 3
    OVERCAST = 4
    RAINY = 5
    SNOWY = 6


class KmaMountainWeatherCode(StrEnum):
    PRECIPITATION_AMOUNT = "PCP"
    PRECIPITATION_PROBABILITY = "POP"
    HUMIDITY = "REH"
    SKY_STATUS = "SKY"
    SNOW_DEPTH = "SNO"
    SUNRISE_AT = "SRE"
    SUNSET_AT = "SSE"
    TEMPERATURE = "TMP"
    WIND_DIRECTION = "VEC"
    WIND_SPEED = "WSD"


class KmaMountainPrecipitationAmount(IntEnum):
    NO_RAINY = 0        # 없음
    WEEK_RAINY = 1      # 3mm 미만의 약한 비
    MIDDLE_RAINY = 2    # 3mm 이상 15mm 미만의 보통 비
    STRONG_RAINY = 3    # 15mm 이상의 강한 비

    @staticmethod
    def kma_str_to_enum(kma_value: str):
        return {
            "강수없음": KmaMountainPrecipitationAmount.NO_RAINY,
            "약한 비": KmaMountainPrecipitationAmount.WEEK_RAINY,
            "보통 비": KmaMountainPrecipitationAmount.MIDDLE_RAINY,
            "강한 비": KmaMountainPrecipitationAmount.STRONG_RAINY,
        }.get(kma_value, KmaMountainPrecipitationAmount.NO_RAINY)

class SnowDepthAmount(IntEnum):
    NO_SNOW = 0     # 없음
    MIDDLE_SNOW = 1 # 보통 눈 (1cm 미만)
    STRONG_SNOW = 2 # 많은 눈 (1cm 이상)

    @staticmethod
    def kma_str_to_enum(kma_value: str):
        return {
            "강설없음": SnowDepthAmount.NO_SNOW,
            "보통 눈": SnowDepthAmount.MIDDLE_SNOW,
            "많은 눈": SnowDepthAmount.STRONG_SNOW,
        }.get(kma_value, SnowDepthAmount.NO_SNOW)


class KmaErrorApiSchema(BaseModel):
    status: int
    message: str


class KmaErrorApiResponse(BaseModel):
    result: KmaErrorApiSchema


class KmaMountainWeatherApiResponseItem(BaseModel):
    base_date: str = Field(alias="baseDate")
    base_time: str = Field(alias="bastTime")
    category: KmaMountainWeatherCode = Field(alias="category")
    forecast_base_date: str = Field(alias="fcstBase")
    forecast_base_time: str = Field(alias="fcstTime")
    forecast_value: str = Field(alias="fcstValue")
    near_location_x: int = Field(alias="nx")
    near_location_y: int = Field(alias="ny")
    lon: str = Field(alias="lon")
    lat: str = Field(alias="lat")
    elevation: str = Field(alias="alt")
    location_name: str = Field(alias="stn_nm")


class KmaMountainWeatherItemParsed(BaseModel):
    forecast_at: datetime = Field(description="현재 시간")
    offset_hours: int = Field(description="x시간 후...")
    precipitation_amount: float = Field(description="강수랑")
    probability_of_precipitation: float = Field(description="강수확률 (%)")
    humidity: float = Field(description="습도 (%)")
    sky_status: KmaMountainSkyStatus = Field(description="하늘 상태")
    snow_depth: SnowDepthAmount = Field(description="적설량 레벨")
    temperature: float = Field(description="기온")
    wind_direction: float = Field(description="풍향 (도)")
    wind_speed: float = Field(description="풍속 레벨")


class KmaMountainWeatherItemBuilder:
    def __init__(self):
        self._data = {}

    def set_forecast_at(self, forecast_at: datetime):
        self._data["forecast_at"] = forecast_at
        return self

    def set_offset_hours(self, target_dt: datetime, forecast_at: datetime):
        target_dt = target_dt.replace(minute=0, second=0, microsecond=0)
        time_detla = forecast_at - target_dt
        seconds = time_detla.total_seconds()
        delta_hours = int(seconds // 3600)

        self._data["offset_hours"] = delta_hours
        return self

    def set_precipitation_amount(self, precipitation_amount: str):
        if precipitation_amount == "강수없음":
            self._data["precipitation_amount"] = 0.0
        else:
            self._data["precipitation_amount"] = float(precipitation_amount)
        return self

    def set_probability_of_precipitation(self, probability_of_precipitation: str):
        self._data["probability_of_precipitation"] = float(probability_of_precipitation)
        return self

    def set_humidity(self, humidity: str):
        self._data["humidity"] = float(humidity)
        return self

    def set_sky_status(self, sky_status: str):
        if "sky_status" not in self._data:
            self._data["sky_status"] = KmaMountainSkyStatus(int(float(sky_status)))
        return self

    def set_snow_depth(self, snow_depth: str):
        self._data["snow_depth"] = SnowDepthAmount.kma_str_to_enum(snow_depth)
        if self._data["snow_depth"] != SnowDepthAmount.NO_SNOW:
            self._data["sky_status"] = KmaMountainSkyStatus.SNOWY
        return self

    def set_temperature(self, temperature: str):
        self._data["temperature"] = float(temperature)
        return self

    def set_wind_direction(self, wind_direction: str):
        self._data["wind_direction"] = float(wind_direction)
        return self

    def set_wind_speed(self, wind_speed: str):
        self._data["wind_speed"] = float(wind_speed)
        return self

    def build(self) -> KmaMountainWeatherItemParsed:
        return KmaMountainWeatherItemParsed(**self._data)
