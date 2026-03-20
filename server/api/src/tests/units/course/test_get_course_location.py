import pytest

from tests.data.course_intervals import POINTS_A_TO_B_DATA, POINTS_B_TO_C_DATA
from tests.data.places import PLACE_A_DATA, PLACE_B_DATA, PLACE_C_DATA
from tests.factories import (
    PlaceFactory,
    CourseIntervalDifficultyFactory,
    CourseIntervalFactory,
    CourseFactory,
    CourseDifficultyFactory,
    CourseStyleFactory,
)
from sqlalchemy.orm import Session
from trailine_api.common.types import CourseLocationType
from trailine_api.repositories.course_repositories import CourseRepository
from trailine_model.models.course import Course


@pytest.fixture
def repo() -> CourseRepository:
    return CourseRepository()


@pytest.fixture
def course_with_intervals() -> Course:
    place_a = PlaceFactory.create(**PLACE_A_DATA)
    place_b = PlaceFactory.create(**PLACE_B_DATA)
    place_c = PlaceFactory.create(**PLACE_C_DATA)

    difficulty = CourseIntervalDifficultyFactory.create(level=1)

    interval_a_to_b = CourseIntervalFactory.create(
        difficulty=difficulty,
        place_a=place_a,
        place_b=place_b,
        points=POINTS_A_TO_B_DATA,
    )
    interval_b_to_c = CourseIntervalFactory.create(
        difficulty=difficulty,
        place_a=place_b,
        place_b=place_c,
        points=POINTS_B_TO_C_DATA,
    )

    course = CourseFactory.create(
        course_difficulty=CourseDifficultyFactory.create(),
        course_style=CourseStyleFactory.create(),
        links=[
            {"interval": interval_a_to_b, "position": 1, "is_reversed": False},
            {"interval": interval_b_to_c, "position": 2, "is_reversed": False},
        ],
    )
    return course


class TestGetCourseLocation:
    def test_returns_none_when_course_id_not_found(self, dbsession: Session, repo: CourseRepository):
        result = repo.get_course_location(dbsession, course_id=9999, location_type=CourseLocationType.START)
        assert result is None

    def test_returns_start_point(self, dbsession: Session, repo: CourseRepository, course_with_intervals: Course):
        result = repo.get_course_location(dbsession, course_with_intervals.id, CourseLocationType.START)
        assert result is not None
        lat, lng = result
        # 시작점: A→B 구간의 첫 번째 좌표
        assert round(lat, 5) == round(POINTS_A_TO_B_DATA[0]["lat"], 5)
        assert round(lng, 5) == round(POINTS_A_TO_B_DATA[0]["lon"], 5)

    def test_returns_middle_point(self, dbsession: Session, repo: CourseRepository, course_with_intervals: Course):
        result = repo.get_course_location(dbsession, course_with_intervals.id, CourseLocationType.MIDDLE)
        assert result is not None
        lat, lng = result
        # 중간지점: A→B + B→C를 이어붙인 전체 라인의 정중앙 부근 (±1 인덱스 허용)
        all_points = POINTS_A_TO_B_DATA + POINTS_B_TO_C_DATA
        mid_index = len(all_points) // 2
        nearby_points = all_points[mid_index - 1:mid_index + 2]
        assert min(p["lat"] for p in nearby_points) <= lat <= max(p["lat"] for p in nearby_points)
        assert min(p["lon"] for p in nearby_points) <= lng <= max(p["lon"] for p in nearby_points)

    def test_returns_end_point(self, dbsession: Session, repo: CourseRepository, course_with_intervals: Course):
        result = repo.get_course_location(dbsession, course_with_intervals.id, CourseLocationType.END)
        assert result is not None
        lat, lng = result
        # 끝점: B→C 구간의 마지막 좌표
        assert round(lat, 5) == round(POINTS_B_TO_C_DATA[-1]["lat"], 5)
        assert round(lng, 5) == round(POINTS_B_TO_C_DATA[-1]["lon"], 5)
