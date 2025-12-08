from sqlalchemy.orm import Session
from starlette.testclient import TestClient
from httpx import Response

from tests.factories import CourseStyleFactory


def _setup_data(session: Session):
    CourseStyleFactory.create_batch(2)
    session.commit()


def test_list_course_style(client: TestClient, dbsession: Session):
    # given
    _setup_data(dbsession)

    # when
    response: Response = client.get("/api/v1/courses/styles")

    # then
    assert response.status_code == 200
    assert len(response.json()) == 2
