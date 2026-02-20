from datetime import datetime, timedelta
from typing import Dict, Any, List, Callable, Optional

from trailine_api.common.db import session_scope
from trailine_api.integrations.external_api import ExternalAPIClient, ExternalApiResponse
from trailine_api.integrations.weather.interface import IWeatherProvider
from trailine_api.integrations.weather.schemas import (
    KmaMountainWeatherApiResponseItem,
    KmaMountainWeatherItemBuilder,
    KmaMountainWeatherCode,
    KmaMountainWeatherItemParsed,
)
from trailine_api.repositories.weather_repositories import IWeatherRepository
from trailine_api.settings import Settings


class KmaMountainWeather(IWeatherProvider):
    weather_repository: IWeatherRepository

    def __init__(self, client: ExternalAPIClient, weather_repository: IWeatherRepository):
        super().__init__(client)
        self.weather_repository = weather_repository

    async def forecast_current(
            self, lat: float, lon: float, target_dt: datetime
    ) -> List[KmaMountainWeatherItemParsed]:
        """
        현재로부터 3시간 이내의 날씨는 1시간 간격으로 가져오는 함수
        """
        # lat, lon과 가장 가까운 산악 코드 조회
        with session_scope() as session:
            mountain_num = self.weather_repository.get_nearest_mountain_area_code(session, lat, lon)

        if not mountain_num:
            return []

        # 기상청 산악 날찌 API 요청 -> Raw한 날씨 데이터 가져오기
        response = await self.client.request(
            method="GET",
            path=Settings.KMA_MOUNTAIN_WEATHER_URL,
            params=self._build_request_params(mountain_num, target_dt),
            success_model=KmaMountainWeatherApiResponseItem,
        )

        if self._has_error_in_response(response):
            # 외부 API 실패 시, Retry 관련 로직 필요
            return []

        # 파싱해서 추출
        return self._parse_short_term_forecast_data(response.data, target_dt)

    def _build_request_params(self, mountain_num: int, target_dt: datetime) -> Dict[str, Any]:
        announcement_dt = self._get_latest_kma_announcement_dt(target_dt)

        return {
            "mountainNum": mountain_num,
            "base_date": announcement_dt.strftime("%Y%m%d"),
            "base_time": announcement_dt.strftime("%H%M")
        }

    def _has_error_in_response(self, response: ExternalApiResponse) -> bool:
        """
        기상청 API 응답 바디를 검사하여 에러 메시지 포함 여부를 확인합니다.
        정상 응답은 리스트 형태이며, 에러 발생 시에는 dict 형태에 'message' 키가 포함됩니다.
        """
        if not response.is_success:
            return True

        raw_data = response.raw_body
        if not isinstance(raw_data, list):
            return True

        return False

    def _parse_short_term_forecast_data(
            self,
            datas: List[KmaMountainWeatherApiResponseItem],
            target_dt: datetime
    ) -> List[KmaMountainWeatherItemParsed]:
        builders: Dict[str, KmaMountainWeatherItemBuilder] = {}

        # target_dt 정규화를 루프 밖에서 한 번만 수행
        normalized_target_dt = target_dt.replace(minute=0, second=0, microsecond=0)

        for data in datas:
            # 날짜 파싱을 한 번만 수행
            try:
                forecast_at = datetime.strptime(
                    data.forecast_base_date + data.forecast_base_time, "%Y%m%d%H%M")
            except (ValueError, TypeError):
                continue

            # 필터링 로직: 긍정형 함수 사용으로 가독성 향상
            if not self._is_within_forecast_window(forecast_at, normalized_target_dt):
                continue

            builder_key = data.forecast_base_date + data.forecast_base_time
            if builder_key not in builders:
                builders[builder_key] = (KmaMountainWeatherItemBuilder()
                                         .set_forecast_at(forecast_at)
                                         .set_offset_hours(target_dt, forecast_at))

            setter = self._select_setter_function(builders[builder_key], data.category)
            if setter:
                setter(data.forecast_value)

        items = [builder.build() for builder in builders.values()]
        items.sort(key=lambda item: item.forecast_at)

        return items

    def _is_within_forecast_window(self, forecast_dt: datetime, target_dt: datetime) -> bool:
        """예측 시간이 기준 시간으로부터 3시간 이내인지 확인"""
        return target_dt <= forecast_dt <= target_dt + timedelta(hours=3)

    def _select_setter_function(
            self,
            builder: KmaMountainWeatherItemBuilder,
            category: KmaMountainWeatherCode
    ) -> Optional[Callable]:
        """
        카테고리에 맞는 데이터 세팅 함수를 선택
        """
        return {
            KmaMountainWeatherCode.PRECIPITATION_AMOUNT: builder.set_precipitation_amount,
            KmaMountainWeatherCode.PRECIPITATION_PROBABILITY: builder.set_probability_of_precipitation,
            KmaMountainWeatherCode.HUMIDITY: builder.set_humidity,
            KmaMountainWeatherCode.SKY_STATUS: builder.set_sky_status,
            KmaMountainWeatherCode.SNOW_DEPTH: builder.set_snow_depth,
            KmaMountainWeatherCode.TEMPERATURE: builder.set_temperature,
            KmaMountainWeatherCode.WIND_DIRECTION: builder.set_wind_direction,
            KmaMountainWeatherCode.WIND_SPEED: builder.set_wind_speed,
        }.get(category, None)

    def _get_latest_kma_announcement_dt(self, target_dt: datetime) -> datetime:
        """
        KMA 발표 시각(02, 05, 08, 11, 14, 17, 20, 23) 중 target_dt와 가장 가까운 과거의 시각을 반환합니다.
        """
        announcement_hours = [2, 5, 8, 11, 14, 17, 20, 23]

        # 현재 시간의 시(hour) 정보를 가져옴
        current_hour = target_dt.hour

        # 발표 시간들 중 current_hour보다 작거나 같은 가장 큰 값을 찾음
        latest_hour = -1
        for hour in reversed(announcement_hours):
            if current_hour >= hour:
                latest_hour = hour
                break

        # 만약 current_hour가 02시 이전이면 전날 23시로 설정
        if latest_hour == -1:
            announcement_dt = target_dt - timedelta(days=1)
            announcement_dt = announcement_dt.replace(hour=23, minute=0, second=0, microsecond=0)
        else:
            announcement_dt = target_dt.replace(hour=latest_hour, minute=0, second=0, microsecond=0)

        return announcement_dt

