from fastapi import APIRouter, Response
from starlette import status

router = APIRouter()


@router.get("/")
async def health_check():
    """ DB 쿼리 실행 예시
    with Session(engine) as session:
        with session.begin():
            from trailine_model.models.user import User
            from sqlalchemy.orm import Session
            from sqlalchemy import select
            from trailine_model.base import engine

            stmt = select(User).where(User.nickname == "recoma")
            user = session.execute(stmt).scalar_one_or_none()
            print("sss")
            print(user)
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
