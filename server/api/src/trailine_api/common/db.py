from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session
from trailine_model.base import SessionLocal


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    트랜잭션을 자동으로 시작하고 커밋/롤백하는 세션 컨텍스트 매니저
    """
    with SessionLocal() as session:
        with session.begin():
            """
            begin()은 빠져나오면 자동으로 session.commit()을 호출
            Exception 발생 시, 알아서 rollback() 수행
            """
            yield session
        # with 문을 빠져나오면 알아서 session.close() 호출
