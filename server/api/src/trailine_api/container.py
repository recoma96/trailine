from dependency_injector import containers, providers
from dependency_injector.providers import Factory

from trailine_api.repositories.course_repositories import CourseRepository, ICourseRepository
from trailine_api.repositories.place_repositories import IPlaceRepository, PlaceRepository
from trailine_api.services.course_services import ICourseServices, CourseServices


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "trailine_api.routers.v1.course"
        ]
    )

    # 1. course_repository provider가 구체 클래스(CourseRepository)를 생성하도록 수정
    course_repository: Factory[ICourseRepository] = Factory(CourseRepository)
    place_repository: Factory[IPlaceRepository] = Factory(PlaceRepository)

    # 2. course_services를 생성할 때, 위에서 정의한 course_repository를 주입하도록 설정
    course_services: Factory[ICourseServices] = Factory(
        CourseServices,
        course_repository=course_repository,
        place_repository=place_repository,
    )
