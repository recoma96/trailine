from fastapi import APIRouter, Response
from starlette import status
# from sqlalchemy.orm import Session
# from trailine_model.base import engine


router = APIRouter()


@router.get("/")
async def health_check():
    """
    with Session(engine) as session:
        with session.begin():
            from trailine_model.models.user import User
            from sqlalchemy import select

            stmt = select(User).where(User.nickname == "recoma")
            user = session.execute(stmt).scalar_one_or_none()
            print(user)
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)
