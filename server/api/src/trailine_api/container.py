import httpx
from dependency_injector import containers
from dependency_injector.providers import Factory, Resource

from trailine_api.integrations.external_api import ExternalAPIClient
from trailine_api.integrations.weather.interface import IWeatherProvider
from trailine_api.integrations.weather.kma_mountain import KmaMountainWeather
from trailine_api.repositories.course_repositories import (
    CourseRepository,
    ICourseRepository,
    ICourseDifficultyRepository,
    CourseDifficultyRepository,
    ICourseStyleRepository,
    CourseStyleRepository
)
from trailine_api.repositories.place_repositories import IPlaceRepository, PlaceRepository
from trailine_api.repositories.weather_repositories import IWeatherRepository, WeatherRepository
from trailine_api.services.course_services import ICourseService, CourseService
from trailine_api.services.weather_services import IWeatherService, WeatherService
from trailine_api.settings import Settings


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "trailine_api.routers.v1.course",
            "trailine_api.routers.v1.weather",
        ]
    )

    # http request client
    http_client: httpx.AsyncClient = Resource(httpx.AsyncClient, timeout=30.0)

    # External Open APIs
    kma_api: Factory[ExternalAPIClient] = Resource( # 기상청 API
        ExternalAPIClient,
        client=http_client,
        base_url=Settings.KMA_API_URL,
        params={"authKey": Settings.KMA_API_AUTH_KEY},
    )

    # Repository
    course_repository: Factory[ICourseRepository] = Factory(CourseRepository)
    course_difficulty_repository: Factory[ICourseDifficultyRepository] = Factory(CourseDifficultyRepository)
    course_style_repository: Factory[ICourseStyleRepository] = Factory(CourseStyleRepository)
    place_repository: Factory[IPlaceRepository] = Factory(PlaceRepository)
    weather_repository: Factory[IWeatherRepository] = Factory(WeatherRepository)

    # Weather APIs
    mountain_weather_api: Factory[IWeatherProvider] = Factory(
        KmaMountainWeather,
        client=kma_api,
        weather_repository=weather_repository,
    )

    # Service
    course_service: Factory[ICourseService] = Factory(
        CourseService,
        course_repository=course_repository,
        place_repository=place_repository,
        course_difficulty_repository=course_difficulty_repository,
        course_style_repository=course_style_repository,
    )
    weather_service: Factory[IWeatherService] = Factory(
        WeatherService,
        mountain_weather_provider=mountain_weather_api,
    )
