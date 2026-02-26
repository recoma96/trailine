from dependency_injector import providers
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from trailine_api.main import app
from trailine_api.common.exc import MountainAreaNotFound
from tests.fakes.weather import FakeMountainWeatherProvider, FakeVillageWeatherProvider
from tests.factories import KmaMountainWeatherAreaFactory


def _override_weather_providers():
    app.container.mountain_weather_api.override(providers.Object(FakeMountainWeatherProvider()))
    app.container.village_weather_api.override(providers.Object(FakeVillageWeatherProvider()))


def _reset_weather_providers():
    app.container.mountain_weather_api.reset_override()
    app.container.village_weather_api.reset_override()


def test_get_weather_current_mountain_ok(client: TestClient, dbsession: Session):
    _override_weather_providers()
    try:
        KmaMountainWeatherAreaFactory.create(latitude=37.5, longitude=127.0, code=1001, name="테스트산")
        dbsession.commit()

        response = client.get(
            "/api/v1/weather/current",
            params={"lat": 37.5, "lon": 127.0, "isMountain": True},
        )

        assert response.status_code == 200
        output = response.json()
        assert "weathers" in output
        assert len(output["weathers"]) > 0
        assert "nowAt" in output["weathers"][0]
        assert "offsetHours" in output["weathers"][0]
        assert "temperature" in output["weathers"][0]
        assert "precipAmount" in output["weathers"][0]
        assert "windSpeed" in output["weathers"][0]
        assert "windDirection" in output["weathers"][0]
        assert "snowDepth" in output["weathers"][0]
        assert "skyStatus" in output["weathers"][0]
        assert "humidity" in output["weathers"][0]
    finally:
        _reset_weather_providers()


def test_get_weather_current_village_ok(client: TestClient, dbsession: Session):
    _override_weather_providers()
    try:
        response = client.get(
            "/api/v1/weather/current",
            params={"lat": 37.5, "lon": 127.0, "isMountain": False},
        )

        assert response.status_code == 200
        output = response.json()
        assert "weathers" in output
        assert len(output["weathers"]) > 0
    finally:
        _reset_weather_providers()


def test_get_weather_current_mountain_not_found(client: TestClient):
    _override_weather_providers()
    try:
        response = client.get(
            "/api/v1/weather/current",
            params={"lat": 37.5, "lon": 127.0, "isMountain": True},
        )

        assert response.status_code == 422
        output = response.json()
        assert output["errorCode"] == MountainAreaNotFound.error_code
        assert output["message"] == MountainAreaNotFound.error_message
    finally:
        _reset_weather_providers()
