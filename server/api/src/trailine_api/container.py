from dependency_injector import containers, providers
from dependency_injector.providers import Factory

from trailine_api.services.course_services import ICourseServices, CourseServices


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "trailine_api.routers.v1.course"
        ]
    )
    course_services: Factory[ICourseServices] = Factory(CourseServices)
