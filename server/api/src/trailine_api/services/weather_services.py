from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List
import asyncio
import logging

from trailine_api.common.cache import RedisCache
from trailine_api.common.db import session_scope
from trailine_api.integrations.weather.interface import IWeatherProvider
from trailine_api.integrations.weather.schemas import DatagoWeatherRainType
from trailine_api.repositories.weather_repositories import IWeatherRepository
from trailine_api.schemas.weather import CurrentWeather, SkyStatusType

_logger = logging.getLogger(__name__)


class IWeatherService(metaclass=ABCMeta):
    mountain_weather_provider: IWeatherProvider
    village_weather_provider: IWeatherProvider
    weather_repository: IWeatherRepository
    cache_client: RedisCache

    def __init__(
            self,
            mountain_weather_provider: IWeatherProvider,
            village_weather_provider: IWeatherProvider,
            weather_repository: IWeatherRepository,
            cache_client: RedisCache
    ):
        self.mountain_weather_provider = mountain_weather_provider
        self.village_weather_provider = village_weather_provider
        self.weather_repository = weather_repository
        self.cache_client = cache_client

    @abstractmethod
    async def get_weather_current(
            self, lat: float, lon: float, target_dt: datetime, is_mountain: bool) -> List[CurrentWeather]:
        pass


class WeatherService(IWeatherService):
    async def get_weather_current(
            self, lat: float, lon: float, target_dt: datetime, is_mountain: bool) -> List[CurrentWeather]:
        if is_mountain:
            # 위/경도에 대한 근처 (기상청) 산악 번호 가져오기
            with session_scope() as session:
                mountain_num = self.weather_repository.get_nearest_mountain_area_code(session, lat, lon)

            # 원래는 데이터가 있음을 보장하지만, 혹시 어떻게 될지 모르니 예외처리
            if mountain_num is None:
                raise ValueError("mountain_num is None")

            # 캐싱여부 확인
            cache_date_key = target_dt.strftime('%Y%m%d%H00')
            cache_key = f"weather:current:location:mountain:{mountain_num}:{cache_date_key}"
            lock_key = f"lock:weather:current:mountain:{mountain_num}"
            cached_weather = await self.cache_client.get_json(cache_key)
            if cached_weather is not None:
                return [CurrentWeather.model_validate(item) for item in cached_weather]

            # 백그라운드(비동기)로 산악지형 데이터 캐싱
            # 추후 해당 코드가 성능이 좋지 않다고 판단될 시, Celery 활용 고려
            lock_token = await self.cache_client.acquire_lock(lock_key, ttl_seconds=30)
            if lock_token is not None:
                asyncio.create_task(
                    self._refresh_mountain_cache(lat, lon, target_dt, cache_key, lock_key, lock_token)
                )

        # 비산악지형 날씨 가져오기
        weather_datas = await self.village_weather_provider.forecast_current(lat, lon, target_dt)
        return [
            CurrentWeather(
                now_at=target_dt.replace(minute=0, second=0, microsecond=0),
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
        """
        공공관리 데이터에서 강수 타입이 눈 관련인지 확인하는 함수
        """
        return rain_type in (
            DatagoWeatherRainType.SNOW_FLURRY,
            DatagoWeatherRainType.SNOWY,
        )

    async def _refresh_mountain_cache(
            self,
            lat: float,
            lon: float,
            target_dt: datetime,
            cache_key: str,
            lock_key: str,
            lock_token: str,
    ) -> None:
        """
        산악지형에 대한 현재 날씨 정보 캐싱
        """
        try:
            weather_datas = await self.mountain_weather_provider.forecast_current(lat, lon, target_dt)
            weathers = [
                CurrentWeather(
                    now_at=target_dt.replace(minute=0, second=0, microsecond=0),
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
            payload = [weather.model_dump(mode="json") for weather in weathers]
            await self.cache_client.set_json(cache_key, payload, ttl_seconds=3600)
        except Exception:
            _logger.exception("Failed to refresh mountain weather cache.")
        finally:
            await self.cache_client.release_lock(lock_key, lock_token)
