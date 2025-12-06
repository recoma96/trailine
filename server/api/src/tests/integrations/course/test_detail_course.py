from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient
import pytest
from httpx import Response

from tests.data.course_intervals import POINTS_A_TO_B_DATA, POINTS_B_TO_C_DATA
from tests.data.places import (
    PLACE_A_DATA,
    PLACE_B_DATA,
    PLACE_C_DATA
)
from tests.factories import (
    PlaceFactory,
    CourseIntervalDifficultyFactory,
    CourseIntervalFactory,
    CourseFactory,
    CourseDifficultyFactory,
    CourseStyleFactory,
    CourseImageFactory,
)


def _setup_data(session: Session):
    # given
    place_a = PlaceFactory.create(**PLACE_A_DATA)
    place_b = PlaceFactory.create(**PLACE_B_DATA)
    place_c = PlaceFactory.create(**PLACE_C_DATA)

    difficulty_lv1 = CourseIntervalDifficultyFactory.create(level=1)
    difficulty_lv2 = CourseIntervalDifficultyFactory.create(level=2)

    interval_a_to_b = CourseIntervalFactory.create(
        difficulty=difficulty_lv1,
        place_a=place_a,
        place_b=place_b,
        points=POINTS_A_TO_B_DATA
    )
    interval_b_to_c = CourseIntervalFactory.create(
        difficulty=difficulty_lv2,
        place_a=place_b,
        place_b=place_c,
        points=POINTS_B_TO_C_DATA
    )

    course = CourseFactory.create(
        name="관악산 일부 코스",
        course_difficulty=CourseDifficultyFactory.create(),
        course_style=CourseStyleFactory.create(),
        links=[
            {"interval": interval_a_to_b, "position": 1},
            {"interval": interval_b_to_c, "position": 2}
        ]
    )


    CourseImageFactory.create(sort_order=1, course_id=course.id)
    CourseImageFactory.create(sort_order=2, course_id=course.id)

    session.commit()


@pytest.mark.parametrize(
    "params, error_code",
    [
        ({"course_id": 1}, 200),
        ({"course_id": 2}, 404),
    ]
)
def test_detail_course(
        client: TestClient,
        dbsession: Session,
        params: Dict,
        error_code: int,
):
    _setup_data(dbsession)

    # when
    response: Response = client.get(f"/api/v1/courses/{params['course_id']}")

    # then
    assert response.status_code == error_code
