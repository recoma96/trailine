from dependency_injector import containers
from dependency_injector.providers import Factory

from trailine_api.repositories.course_repositories import (
    CourseRepository,
    ICourseRepository,
    ICourseDifficultyRepository,
    CourseDifficultyRepository,
    ICourseStyleRepository,
    CourseStyleRepository
)
from trailine_api.repositories.place_repositories import IPlaceRepository, PlaceRepository
from trailine_api.services.course_services import ICourseService, CourseService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "trailine_api.routers.v1.course"
        ]
    )

    # Repository
    course_repository: Factory[ICourseRepository] = Factory(CourseRepository)
    course_difficulty_repository: Factory[ICourseDifficultyRepository] = Factory(CourseDifficultyRepository)
    course_style_repository: Factory[ICourseStyleRepository] = Factory(CourseStyleRepository)
    place_repository: Factory[IPlaceRepository] = Factory(PlaceRepository)

    # Service
    course_services: Factory[ICourseService] = Factory(
        CourseService,
        course_repository=course_repository,
        place_repository=place_repository,
        course_difficulty_repository=course_difficulty_repository,
        course_style_repository=course_style_repository,
    )
