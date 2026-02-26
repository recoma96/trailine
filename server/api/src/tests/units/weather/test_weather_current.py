from contextlib import contextmanager
from datetime import datetime
from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock

import pytest

from trailine_api.common.cache import RedisCache
from trailine_api.common.exc import MountainAreaNotFound
from trailine_api.integrations.weather.schemas import (
    DatagoShortTermWeatherParsed,
    DatagoSkyStatus,
    DatagoWeatherRainType,
    KmaMountainWeatherItemParsed,
    KmaMountainSkyStatus,
    SnowDepthAmount,
)
from trailine_api.services import weather_services
from trailine_api.services.weather_services import WeatherService
from trailine_api.schemas.weather import CurrentWeather


@dataclass
class _Deps:
    service: WeatherService
    cache_client: RedisCache
    weather_repository: Mock
    mountain_weather_provider: Mock
    village_weather_provider: Mock


@pytest.fixture
def deps(monkeypatch) -> _Deps:
    @contextmanager
    def _fake_session_scope():
        yield None

    monkeypatch.setattr(weather_services, "session_scope", _fake_session_scope)

    cache_client = Mock(spec=RedisCache)
    cache_client.get_json = AsyncMock()
    cache_client.set_json = AsyncMock()
    cache_client.acquire_lock = AsyncMock()
    cache_client.release_lock = AsyncMock()
    cache_client.build_lock_key = Mock(side_effect=lambda key: f"lock:{key}")

    weather_repository = Mock()
    mountain_weather_provider = Mock()
    mountain_weather_provider.forecast_current = AsyncMock()
    village_weather_provider = Mock()
    village_weather_provider.forecast_current = AsyncMock()

    service = WeatherService(
        mountain_weather_provider=mountain_weather_provider,
        village_weather_provider=village_weather_provider,
        weather_repository=weather_repository,
        cache_client=cache_client,
    )

    return _Deps(
        service=service,
        cache_client=cache_client,
        weather_repository=weather_repository,
        mountain_weather_provider=mountain_weather_provider,
        village_weather_provider=village_weather_provider,
    )


def _build_datago_weather(target_dt: datetime) -> DatagoShortTermWeatherParsed:
    return DatagoShortTermWeatherParsed(
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


def _build_mountain_weather(target_dt: datetime) -> KmaMountainWeatherItemParsed:
    return KmaMountainWeatherItemParsed(
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


@pytest.mark.asyncio
async def test_get_weather_current_mountain_none_raises(deps: _Deps):
    deps.weather_repository.get_nearest_mountain_area_code.return_value = None

    with pytest.raises(MountainAreaNotFound):
        await deps.service.get_weather_current(37.5, 127.0, datetime.now(), True)


@pytest.mark.asyncio
async def test_get_weather_current_mountain_cache_hit_returns(deps: _Deps):
    deps.weather_repository.get_nearest_mountain_area_code.return_value = 1001
    sample = CurrentWeather(
        now_at=datetime.now(),
        offset_hours=0,
        temperature=3.0,
        precip_amount=0.0,
        wind_speed=1.0,
        wind_dir=90.0,
        snow_depth=0,
        sky_status="sunny",
        humidity=40.0,
    )
    deps.cache_client.get_json.return_value = [sample.model_dump(mode="json")]

    result = await deps.service.get_weather_current(37.5, 127.0, datetime.now(), True)

    assert len(result) == 1
    deps.village_weather_provider.forecast_current.assert_not_called()
    deps.mountain_weather_provider.forecast_current.assert_not_called()


@pytest.mark.asyncio
async def test_get_weather_current_mountain_cache_miss_lock_acquired_creates_task(deps: _Deps, monkeypatch):
    deps.weather_repository.get_nearest_mountain_area_code.return_value = 1001
    deps.cache_client.get_json.return_value = None
    deps.cache_client.acquire_lock.return_value = "token"
    deps.village_weather_provider.forecast_current.return_value = [_build_datago_weather(datetime.now())]

    create_task_mock = Mock()
    monkeypatch.setattr(weather_services.asyncio, "create_task", create_task_mock)

    await deps.service.get_weather_current(37.5, 127.0, datetime.now(), True)

    assert create_task_mock.called


@pytest.mark.asyncio
async def test_get_weather_current_mountain_cache_miss_lock_failed_no_task(deps: _Deps, monkeypatch):
    deps.weather_repository.get_nearest_mountain_area_code.return_value = 1001
    deps.cache_client.get_json.return_value = None
    deps.cache_client.acquire_lock.return_value = None
    deps.village_weather_provider.forecast_current.return_value = [_build_datago_weather(datetime.now())]

    create_task_mock = Mock()
    monkeypatch.setattr(weather_services.asyncio, "create_task", create_task_mock)

    await deps.service.get_weather_current(37.5, 127.0, datetime.now(), True)

    create_task_mock.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_mountain_cache_success_sets_cache(deps: _Deps):
    deps.mountain_weather_provider.forecast_current.return_value = [
        _build_mountain_weather(datetime.now())
    ]

    await deps.service._refresh_mountain_cache(
        37.5,
        127.0,
        datetime.now(),
        "weather:current:location:mountain:1:202602260900",
        "lock:weather:current:location:mountain:1:202602260900",
        "token",
    )

    deps.cache_client.set_json.assert_called_once()
    deps.cache_client.release_lock.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_mountain_cache_failure_releases_lock(deps: _Deps):
    deps.mountain_weather_provider.forecast_current.side_effect = RuntimeError("boom")

    await deps.service._refresh_mountain_cache(
        37.5,
        127.0,
        datetime.now(),
        "weather:current:location:mountain:1:202602260900",
        "lock:weather:current:location:mountain:1:202602260900",
        "token",
    )

    deps.cache_client.set_json.assert_not_called()
    deps.cache_client.release_lock.assert_called_once()
