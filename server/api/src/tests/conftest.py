import pytest
from fastapi.testclient import TestClient

# 사용자의 애플리케이션 구조에 맞게 임포트 경로를 수정해야 합니다.
# 예: from api.src.main import app
from trailine_api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
