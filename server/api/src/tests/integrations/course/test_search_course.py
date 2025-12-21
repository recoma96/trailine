from typing import Dict

from sqlalchemy.orm import Session
from starlette.testclient import TestClient
import pytest
from httpx import Response

from tests.integrations.common import setup_course_data_no_1


def _setup_data(session: Session):
    setup_course_data_no_1()
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

        assert output["courses"][0]["loadAddresses"] == ["경기도 과천시 특정도로명주소-1", "경기도 과천시 특정도로명주소-2"]
        assert output["courses"][0]["roadAddresses"] == ["경기도 과천시 특정지번주소-1", "경기도 과천시 특정지번주소-2"]
