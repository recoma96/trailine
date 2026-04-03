from abc import ABCMeta, abstractmethod
from typing import List, Tuple
from datetime import datetime, timedelta

from fastapi import HTTPException
from starlette import status

from trailine_api.common.db import session_scope
from trailine_api.common.types import CourseLocationType
from trailine_api.common.utils import latlon_to_grid
from trailine_api.externals.datago import IKmaMidLandForecastAPI, IKmaMidLandTemperatureAPI
from trailine_api.repositories.course_repositories import ICourseRepository
from trailine_api.repositories.weather_repositories import IWeatherRepository
from trailine_api.schemas.weather import WeatherForecastItemSchema


MID_FORECAST_MIN_DAY = 5  # 기상청 중기예보 시작일 (5일 후부터)
DATE_FORMAT = "%Y-%m-%d"


class IWeatherService(metaclass=ABCMeta):
    _course_repository: ICourseRepository
    _weather_repository: IWeatherRepository
    _kma_mid_forecast_api: IKmaMidLandForecastAPI
    _kma_mid_temperature_api: IKmaMidLandTemperatureAPI

    def __init__(
            self,
            course_repository: ICourseRepository,
            weather_repository: IWeatherRepository,
            kma_mid_forecast_api: IKmaMidLandForecastAPI,
            kma_mid_temperature_api: IKmaMidLandTemperatureAPI
    ):
        self._course_repository = course_repository
        self._weather_repository = weather_repository
        self._kma_mid_forecast_api = kma_mid_forecast_api
        self._kma_mid_temperature_api = kma_mid_temperature_api

    @abstractmethod
    def get_forecasts(self, course_id: int, days: int) -> List[WeatherForecastItemSchema]:
        """
        특정 위치/주소애 대한 장기 일기예보 정보를 가져오는 함수
        """
        pass


class WeatherService(IWeatherService):
    def get_forecasts(self, course_id: int, days: int) -> List[WeatherForecastItemSchema]:
        status_code, temp_code, nx, ny = self._get_course_weather_info(course_id)

        results: List[WeatherForecastItemSchema] = []

        # days <= 4: 기상청 단기예보 활용 (TODO)

        # days >= 5: 중기예보
        if days >= MID_FORECAST_MIN_DAY:
            results.extend(self._build_mid_forecasts(status_code, temp_code, days))

        return results

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

            nx, ny = latlon_to_grid(
                *self._course_repository.get_course_location(session, course_id, CourseLocationType.MIDDLE),
            )

        return kma_mid_status_code, kma_mid_temp_code, nx, ny

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

            results.append(
                WeatherForecastItemSchema(
                    date=forecast_date.strftime(DATE_FORMAT),
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
