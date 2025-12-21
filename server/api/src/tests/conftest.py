from typing import Generator, Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from trailine_api.main import app
from trailine_model.base import engine as dbengine, Base, SessionLocal

from .factories import BaseFactory


@pytest.fixture(scope="function")
def dbsession() -> Generator[Session, Any, None]:
    connection = dbengine.connect()
    session = SessionLocal(bind=connection)

    yield session

    # 테스트가 끝난 후 실행되는 정리(cleanup) 로직
    try:
        # 1. 열려있는 트랜잭션이 있다면 모두 롤백하여 연결을 깨끗한 상태로 만듭니다.
        session.rollback()

        # 2. 초기화에서 제외할 테이블 목록을 정의합니다. (예: alembic 마이그레이션 테이블)
        excluded_tables = {"alembic_version", "spatial_ref_sys"}

        # 3. Base.metadata에 등록된 모든 테이블 이름을 가져옵니다.
        table_names = Base.metadata.tables.keys()
        tables_to_truncate = [tbl for tbl in table_names if tbl not in excluded_tables]

        if tables_to_truncate:
            # 4. TRUNCATE 구문을 실행하여 모든 테이블 데이터를 삭제하고 ID를 초기화합니다.
            truncate_query = f"TRUNCATE TABLE {', '.join(tables_to_truncate)} RESTART IDENTITY CASCADE;"
            session.execute(text(truncate_query))
            session.commit()
    finally:
        session.close()
        connection.close()


@pytest.fixture(scope="function")
def client(dbsession: Session):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function", autouse=True)
def _bind_factories_to_session(dbsession: Session) -> None:
    """
    테스트 세션 시작 시 모든 팩토리의 세션을 바인딩
    """
    for factory_cls in BaseFactory.__subclasses__():
        factory_cls._meta.sqlalchemy_session = dbsession
