from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable

from trailine_api.integrations.external_api import ExternalApiResponse
from trailine_api.integrations.weather.interface import IWeatherProvider
from trailine_api.integrations.weather.schemas import (
    DatagoShortTermWeatherApiResponse,
    DatagoShortTermWeatherItem,
    DatagoShortTermWeatherParsed,
    DatagoShortTermWeatherItemBuilder,
    DatagoShortTermWeatherCode,
)
from trailine_api.integrations.weather.utils import is_within_forecast_window, latlon_to_kma_grid
from trailine_api.settings import Settings


class DataGoWeather(IWeatherProvider):
    async def get_current_weather(
            self, lat: float, lon: float, target_dt: datetime) -> List:

        nx, ny = latlon_to_kma_grid(lat, lon)
        response = await self.client.request(
            method="GET",
            path=Settings.DATAGO_VILEAGE_WEATHER_URL,
            params=self._build_forecast_curent_request_params(nx, ny, target_dt),
            success_model=DatagoShortTermWeatherApiResponse,
        )

        if self._has_error_in_response(response):
            return []

        response_data = response.data

        if response_data is None:
            return []

        if not isinstance(response_data, DatagoShortTermWeatherApiResponse):
            return []

        return self._parse_short_term_forecast_data(response_data.response.body.items.item, target_dt)

    def _build_forecast_curent_request_params(self, nx: int, ny: int, target_dt: datetime) -> Dict[str, Any]:
        return {
            "numOfRows": 60,    # 고정 60개
            "base_date": target_dt.strftime("%Y%m%d"),
            "base_time": (target_dt - timedelta(hours=1)).strftime("%H%M"),
            "nx": nx,
            "ny": ny,
            "dataType": "JSON",
        }

    def _has_error_in_response(self, response: ExternalApiResponse) -> bool:
        if not response.is_success:
            return True

        data = response.data
        if not isinstance(data, DatagoShortTermWeatherApiResponse):
            return True

        return data.response.header.result_code != "00"

    def _parse_short_term_forecast_data(
        self,
        datas: List[DatagoShortTermWeatherItem],
        target_dt: datetime,
    ) -> List[DatagoShortTermWeatherParsed]:
        builders: Dict[str, DatagoShortTermWeatherItemBuilder] = {}
        normalized_target_dt = target_dt.replace(minute=0, second=0, microsecond=0)

        for data in datas:
            forecast_at = datetime.strptime(data.forecast_date + data.forecast_time, "%Y%m%d%H%M")
            if not is_within_forecast_window(normalized_target_dt, forecast_at):
                continue

            builder_key = data.forecast_date + data.forecast_time
            if not builder_key in builders:
                builders[builder_key] = (DatagoShortTermWeatherItemBuilder()
                                         .set_forecast_at(forecast_at)
                                         .set_offset_hours(target_dt, forecast_at))

            setter = self._select_setter_function(builders[builder_key], data.category)
            if setter:
                setter(data.forecast_value)

        items = [builder.build() for builder in builders.values()]
        items.sort(key=lambda item: item.offset_hours)

        return items

    def _select_setter_function(
            self,
            builder: DatagoShortTermWeatherItemBuilder,
            category: DatagoShortTermWeatherCode
    ) -> Optional[Callable]:
        CodeType = DatagoShortTermWeatherCode
        return {
            CodeType.TEMPERATURE: builder.set_temperature,
            CodeType.PRECIPITATION_AMOUNT: builder.set_precipitation_amount,
            CodeType.SKY_STATUS: builder.set_sky_status,
            CodeType.MERIDIONAL_WIND: builder.set_meridional_wind_component,
            CodeType.ZONAL_WIND: builder.set_zonal_wind_component,
            CodeType.HUMIDITY: builder.set_humidity,
            CodeType.RAIN_TYPE: builder.set_rain_type,
            CodeType.THUNDERSTROKE: builder.set_thunderstroke,
            CodeType.WIND_DIRECTION: builder.set_wind_direction,
            CodeType.WIND_SPEED: builder.set_wind_speed,
        }.get(category, None)
