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
