from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Dict
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import HTTPException
from starlette import status

from trailine_api.common.cache import RedisCache
from trailine_api.common.db import session_scope
from trailine_api.common.types import CourseLocationType, DatagoShortForecastRainCondition, SkyCondition
from trailine_api.common.utils import latlon_to_grid
from trailine_api.externals.datago import IKmaMidLandForecastAPI, IKmaMidLandTemperatureAPI, IKmaShortForecastAPI
from trailine_api.repositories.course_repositories import ICourseRepository
from trailine_api.repositories.weather_repositories import IWeatherRepository
from trailine_api.schemas.weather import DAY_OF_WEEK_KO_LIST, DAY_OF_WEEK_LIST, ShortForecastItem, WeatherForecastItemSchema


MID_FORECAST_MIN_DAY = 5  # 기상청 중기예보 시작일 (5일 후부터)
CACHE_TTL_SECONDS = 3600 * 3  # 1시간 + 3시간
DATE_FORMAT = "%Y-%m-%d"


class IWeatherService(metaclass=ABCMeta):
    _cache: RedisCache
    _course_repository: ICourseRepository
    _weather_repository: IWeatherRepository
    _kma_mid_forecast_api: IKmaMidLandForecastAPI
    _kma_mid_temperature_api: IKmaMidLandTemperatureAPI
    _kma_short_forecast_api: IKmaShortForecastAPI

    def __init__(
            self,
            cache: RedisCache,
            course_repository: ICourseRepository,
            weather_repository: IWeatherRepository,
            kma_mid_forecast_api: IKmaMidLandForecastAPI,
            kma_mid_temperature_api: IKmaMidLandTemperatureAPI,
            kma_short_forecast_api: IKmaShortForecastAPI
    ):
        self._cache = cache
        self._course_repository = course_repository
        self._weather_repository = weather_repository
        self._kma_mid_forecast_api = kma_mid_forecast_api
        self._kma_mid_temperature_api = kma_mid_temperature_api
        self._kma_short_forecast_api = kma_short_forecast_api

    @abstractmethod
    async def get_forecasts(
        self, course_id: int, days: int
    ) -> Tuple[datetime, List[WeatherForecastItemSchema]]:
        """
        특정 위치/주소애 대한 장기 일기예보 정보를 가져오는 함수
        """
        pass


class WeatherService(IWeatherService):
    async def get_forecasts(
        self, course_id: int, days: int
    ) -> Tuple[datetime, List[WeatherForecastItemSchema]]:
        # 발표 시각 계산 (네트워크 호출 없이 시간 계산만 수행)
        published_at = self._resolve_published_at(days)

        # 캐싱된 데이터 가져오기 (발표 시각이 바뀌면 키도 자연스럽게 무효화)
        cache_key = f"weather:course:{course_id}:{days}:{published_at.strftime('%Y%m%d%H%M')}"
        cached = await self._cache.get_json(cache_key)
        if isinstance(cached, list):
            return published_at, [WeatherForecastItemSchema(**item) for item in cached]

        # 캐싱된 데이터 없으면 직접 조회
        status_code, temp_code, nx, ny = self._get_course_weather_info(course_id)

        results: List[WeatherForecastItemSchema] = []

        # days <= 4: 기상청 단기예 활용
        results.extend(self._build_short_forecasts(nx, ny, days))

        # days >= 5: 중기예보 활용
        if days >= MID_FORECAST_MIN_DAY:
            results.extend(self._build_mid_forecasts(status_code, temp_code, days))

        # 캐시에 데이터 올리기
        await self._cache.set_json(
            cache_key,
            [item.model_dump(by_alias=True) for item in results],
            ttl_seconds=CACHE_TTL_SECONDS,
        )

        return published_at, results

    def _resolve_published_at(self, days: int) -> datetime:
        """요청 days에 따라 사용된 예보 API의 발표 시각을 결정한다.

        days < 5인 경우는 단기예보만 사용하므로 단기예보 발표 시각을 그대로 사용하고,
        days >= 5인 경우 단기/중기 발표 시각 중 가장 최근 시각을 사용한다.
        """
        short_published_at = self._kma_short_forecast_api.get_published_at()
        if days < MID_FORECAST_MIN_DAY:
            return short_published_at

        mid_published_at = self._kma_mid_forecast_api.get_published_at()
        return max(short_published_at, mid_published_at)

    def _get_course_weather_info(self, course_id: int) -> Tuple[str, str, int, int]:
        """DB에서 기상청 코드와 좌표를 조회한다."""
        with session_scope() as session:
            try:
                kma_mid_status_code, kma_mid_temp_code = (
                    self._weather_repository.get_mid_land_forecast_codes(session, course_id)
                )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="코스를 찾을 수 없어요."
                )

            if not kma_mid_status_code or not kma_mid_temp_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="날씨 정보를 찾을 수 없어요."
                )

            location = self._course_repository.get_course_location(session, course_id, CourseLocationType.MIDDLE)
            if location is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="코스 위치 정보를 찾을 수 없어요."
                )
            nx, ny = latlon_to_grid(*location)

        return kma_mid_status_code, kma_mid_temp_code, nx, ny

    _SKY_CONDITION_PRIORITY = {
        SkyCondition.CLEAR: 0,
        SkyCondition.CLOUDY: 1,
        SkyCondition.RAIN: 2,
        SkyCondition.SNOW: 3,
    }

    def _build_short_forecasts(self, nx: int, ny: int, days: int) -> List[WeatherForecastItemSchema]:
        """단기예보 API를 호출하고 응답을 조합한다"""
        short_forecasts = self._kma_short_forecast_api.call(nx, ny, days)

        daily: Dict[str, List[ShortForecastItem]] = defaultdict(list)

        # 예보 데이터를 날짜별로 그룹핑
        for item in short_forecasts:
            date_key = item.forecast_date.strftime(DATE_FORMAT)
            daily[date_key].append(item)

        results: List[WeatherForecastItemSchema] = []
        for date_key in sorted(daily):
            items = daily[date_key]
            weekday = datetime.strptime(date_key, DATE_FORMAT).weekday()

            results.append(
                WeatherForecastItemSchema(
                    date=date_key,
                    dayOfWeek=DAY_OF_WEEK_LIST[weekday],
                    dayOfWeekKo=DAY_OF_WEEK_KO_LIST[weekday],
                    minTemperature=min(item.temperature for item in items),
                    maxTemperature=max(item.temperature for item in items),
                    precipitationProbability=max(item.rain_probability for item in items),
                    skyCondition=self._resolve_daily_sky_condition(items),
                )
            )

        return results

    def _resolve_daily_sky_condition(self, items: List[ShortForecastItem]) -> SkyCondition:
        """시간별 예보에서 하루의 대표 하늘 상태를 결정한다."""
        worst = SkyCondition.CLEAR
        for item in items:
            if item.rain_condition != DatagoShortForecastRainCondition.NONE:
                condition = item.rain_condition.to_sky_condition()
            else:
                condition = item.sky_condition.to_sky_condition()

            if self._SKY_CONDITION_PRIORITY[condition] > self._SKY_CONDITION_PRIORITY[worst]:
                worst = condition

        return worst

    def _build_mid_forecasts(
        self, status_code: str, temp_code: str, days: int
    ) -> List[WeatherForecastItemSchema]:
        """중기예보 API를 호출하고 응답을 조합한다."""
        mid_forecasts = self._kma_mid_forecast_api.call(status_code)
        mid_temperatures = self._kma_mid_temperature_api.call(temp_code)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        results: List[WeatherForecastItemSchema] = []

        for i in range(MID_FORECAST_MIN_DAY, days + 1):
            raw_i = i - MID_FORECAST_MIN_DAY
            forecast_date = today + timedelta(days=i)

            weekday = forecast_date.weekday()
            results.append(
                WeatherForecastItemSchema(
                    date=forecast_date.strftime(DATE_FORMAT),
                    dayOfWeek=DAY_OF_WEEK_LIST[weekday],
                    dayOfWeekKo=DAY_OF_WEEK_KO_LIST[weekday],
                    minTemperature=mid_temperatures[raw_i].min_temperature,
                    maxTemperature=mid_temperatures[raw_i].max_temperature,
                    precipitationProbability=max(
                        mid_forecasts[raw_i].rain_probability_am,
                        mid_forecasts[raw_i].rain_probability_pm
                    ),
                    skyCondition=mid_forecasts[raw_i].sky_condition_am.to_sky_condition(),
                )
            )

        return results
