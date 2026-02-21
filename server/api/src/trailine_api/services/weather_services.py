from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List

from trailine_api.integrations.weather.interface import IWeatherProvider
from trailine_api.integrations.weather.schemas import DatagoWeatherRainType
from trailine_api.schemas.weather import CurrentWeather, SkyStatusType


class IWeatherService(metaclass=ABCMeta):
    mountain_weather_provider: IWeatherProvider

    def __init__(
            self,
            mountain_weather_provider: IWeatherProvider,
            village_weather_provider: IWeatherProvider
    ):
        self.mountain_weather_provider = mountain_weather_provider
        self.village_weather_provider = village_weather_provider

    @abstractmethod
    async def get_weather_current(
            self, lat: float, lon: float, target_dt: datetime, is_mountain: bool) -> List[CurrentWeather]:
        pass


class WeatherService(IWeatherService):
    async def get_weather_current(
            self, lat: float, lon: float, target_dt: datetime, is_mountain: bool):
        # TODO 캐싱된 데이터가 있는지 확인하는 로직 필요

        if is_mountain:
            weather_datas = await self.mountain_weather_provider.forecast_current(lat, lon, target_dt)
            return [
                CurrentWeather(
                    now_at=target_dt,
                    offset_hours=weather_data.offset_hours,
                    temperature=weather_data.temperature,
                    precip_amount=weather_data.precipitation_amount,
                    wind_speed=weather_data.wind_speed,
                    wind_dir=weather_data.wind_direction,
                    snow_depth=weather_data.snow_depth,
                    sky_status=SkyStatusType.get_from_kma_mountain(weather_data.sky_status),
                    humidity=weather_data.humidity,
                )
                for weather_data in weather_datas
            ]
        else:
            weather_datas = await self.village_weather_provider.forecast_current(lat, lon, target_dt)
            return [
                CurrentWeather(
                    now_at=target_dt,
                    offset_hours=weather_data.offset_hours,
                    temperature=weather_data.temperature,
                    precip_amount=weather_data.precipitation_amount,
                    wind_speed=weather_data.wind_speed,
                    wind_dir=weather_data.wind_direction,
                    snow_depth=weather_data.precipitation_amount if self._check_is_snowy_in_datago(weather_data.rain_type) else 0,
                    sky_status=SkyStatusType.get_from_datago(weather_data.sky_status, weather_data.rain_type),
                    humidity=weather_data.humidity,
                )
                for weather_data in weather_datas
            ]

    def _check_is_snowy_in_datago(self, rain_type: DatagoWeatherRainType) -> bool:
        return rain_type in (
            DatagoWeatherRainType.SNOW_FLURRY,
            DatagoWeatherRainType.SNOWY,
        )
