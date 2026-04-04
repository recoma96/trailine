from dependency_injector import containers
from dependency_injector.providers import Factory, Singleton, Resource

from trailine_api.common.cache import cache
from trailine_api.config import Config
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
from trailine_api.externals.datago import IKmaMidLandForecastAPI, KmaMidLandForecastAPI, IKmaMidLandTemperatureAPI, \
    KmaMidLandTemperatureAPI, IKmaShortForecastAPI, KmaShortForecastAPI
from trailine_api.services.course_services import ICourseService, CourseService
from trailine_api.services.weather_services import IWeatherService, WeatherService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "trailine_api.routers.v1.course"
        ]
    )

    # External
    kma_mid_forecast_api: Singleton[IKmaMidLandForecastAPI] = Singleton(
        KmaMidLandForecastAPI,
        service_key=Config.DATAGO_SERVICE_KEY
    )
    kma_mid_temperature_api: Singleton[IKmaMidLandTemperatureAPI] = Singleton(
        KmaMidLandTemperatureAPI,
        service_key=Config.DATAGO_SERVICE_KEY
    )
    kma_short_forecast_api: Singleton[IKmaShortForecastAPI] = Singleton(
        KmaShortForecastAPI,
        service_key=Config.DATAGO_SERVICE_KEY
    )

    # Repository
    course_repository: Factory[ICourseRepository] = Factory(CourseRepository)
    course_difficulty_repository: Factory[ICourseDifficultyRepository] = Factory(CourseDifficultyRepository)
    course_style_repository: Factory[ICourseStyleRepository] = Factory(CourseStyleRepository)
    place_repository: Factory[IPlaceRepository] = Factory(PlaceRepository)
    weather_repository: Factory[IWeatherRepository] = Factory(WeatherRepository)

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
        cache=cache,
        weather_repository=weather_repository,
        course_repository=course_repository,
        kma_mid_forecast_api=kma_mid_forecast_api,
        kma_mid_temperature_api=kma_mid_temperature_api,
        kma_short_forecast_api=kma_short_forecast_api,
    )
