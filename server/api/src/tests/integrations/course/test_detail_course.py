from typing import Dict, Tuple

from sqlalchemy.orm import Session
from starlette.testclient import TestClient
import pytest
from httpx import Response

from tests.integrations.common import setup_course_data_no_1


@pytest.fixture(scope="function")
def setup_data(dbsession: Session):
    total_length, duration = setup_course_data_no_1()
    dbsession.commit()
    return total_length, duration


@pytest.mark.parametrize(
    "params, error_code",
    [
        ({"course_id": 1}, 200),
        ({"course_id": 2}, 404),
    ]
)
def test_detail_course(
        client: TestClient,
        setup_data: Tuple[float, int],
        params: Dict,
        error_code: int,
):
    # when
    response: Response = client.get(f"/api/v1/courses/{params['course_id']}")

    # then
    assert response.status_code == error_code
    if response.status_code == 200:
        result = response.json()
        expected_length, expected_duration = setup_data
        assert result["length"] == expected_length
        assert result["duration"] == expected_duration
