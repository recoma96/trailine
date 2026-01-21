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
    "params, error_code",
    [
        ({"course_id": 1}, 200),
        ({"course_id": 2}, 404),
    ]
)
def test_search_course_interval(client: TestClient, dbsession: Session, params: Dict, error_code: int):
    _setup_data(dbsession)

    # when
    response: Response = client.get(f"/api/v1/courses/{params['course_id']}/intervals")

    # then
    assert response.status_code == error_code

    if error_code == 200:
        result = response.json()
        assert result["intervalCount"] == 3

        # 정방향 / 역방향에 대한 설명이 달라지는지 비교
        # 0, 1번은 정방향, 2번은 역방향이다
        output_intervals = result["intervals"]
        assert output_intervals[0]["description"] == "정방향 설명"
        assert output_intervals[1]["description"] == "정방향 설명"
        assert output_intervals[2]["description"] == "역방향 설명"
