from fastapi import APIRouter, Response
from starlette import status


router = APIRouter()


@router.get("/")
async def health_check():
    return Response(status_code=status.HTTP_204_NO_CONTENT)
