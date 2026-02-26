from datetime import datetime

from trailine_api.integrations.weather.schemas import (
    DatagoShortTermWeatherParsed,
    DatagoSkyStatus,
    DatagoWeatherRainType,
    KmaMountainWeatherItemParsed,
    KmaMountainSkyStatus,
    SnowDepthAmount,
)


class FakeMountainWeatherProvider:
    async def forecast_current(self, lat: float, lon: float, target_dt: datetime):
        return [
            KmaMountainWeatherItemParsed(
                forecast_at=target_dt,
                offset_hours=0,
                precipitation_amount=0.0,
                probability_of_precipitation=0.0,
                humidity=50.0,
                sky_status=KmaMountainSkyStatus.SUNNY,
                snow_depth=SnowDepthAmount.NO_SNOW,
                temperature=5.0,
                wind_direction=90.0,
                wind_speed=1.2,
            )
        ]


class FakeVillageWeatherProvider:
    async def forecast_current(self, lat: float, lon: float, target_dt: datetime):
        return [
            DatagoShortTermWeatherParsed(
                forecast_at=target_dt,
                offset_hours=0,
                precipitation_amount=0.0,
                sky_status=DatagoSkyStatus.SUNNY,
                zonal_wind_component=0.1,
                meridional_wind_component=0.1,
                humidity=45.0,
                rain_type=DatagoWeatherRainType.NO_RAINY,
                thunderstroke=0,
                temperature=4.0,
                wind_direction=180.0,
                wind_speed=1.0,
            )
        ]
