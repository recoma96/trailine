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

    CourseFactory.create(
        name="관악산 일부 코스",
        course_difficulty=CourseDifficultyFactory.create(),
        course_style=CourseStyleFactory.create(),
        links=[
            {"interval": interval_a_to_b, "position": 1},
            {"interval": interval_b_to_c, "position": 2}
        ]
    )

    session.commit()


@pytest.mark.parametrize(
    "params, expected_count",
    [
        ({}, 1),
        ({"difficulty": [1]}, 1),   # 생성된 코스 난이도 중 ID가 1인 코스 데이터는 한개다
        ({"difficulty": [2]}, 0),   # 생성된 코스 난이도 중 ID가 1인 코스 데이터는 없다
        ({"word": "관악"}, 1),       # 코스 연관검색 -> 관악으로 검색이 되어야 한다
        ({"word": "-1"}, 1),        # 주소 연관검색 -> 지번주소-1, 도로명주소-1이 있음로 검색이 되어야 한다
        ({"word": "-3"}, 0),        # 주소 연관검색 -> 지번주소-3 인 데이터는 없다
        ({"courseStyle": 1}, 1),    # 코스 스타일 검색 ID가 1인 코스 스타일이 포함된 데이터는 한개다
        ({"courseStyle": 2}, 0),    # 코스 스타일 검색 ID가 2인 코스 스타일이 포함된 데이터는 없다
    ]
)
def test_search_course_list(
        client: TestClient,
        dbsession: Session,
        params: Dict,
        expected_count: int,
):
    _setup_data(dbsession)

    # when
    response: Response = client.get("/api/v1/courses", params=params)

    # then
    assert response.status_code == 200
    output = response.json()

    assert output["total"] == expected_count

    if expected_count > 0:
        assert "difficulty" in output["courses"][0]
        assert "courseStyle" in output["courses"][0]

        assert output["courses"][0]["loadAddress"] == ["경기도 과천시 특정도로명주소-1", "경기도 과천시 특정도로명주소-2"]
        assert output["courses"][0]["roadAddress"] == ["경기도 과천시 특정지번주소-1", "경기도 과천시 특정지번주소-2"]
