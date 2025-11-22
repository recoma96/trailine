from typing import List, Annotated, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Query
from fastapi import status
from fastapi.params import Depends

from trailine_api.container import Container
from trailine_api.services.course_services import ICourseServices


router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[str],
    summary="연관 검색어 조회",
)
@inject
def get_courses(
    course_service: Annotated[ICourseServices, Depends(Provide[Container.course_services])],
    word: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        title="검색어 (코스명 또는 주소)",
        description="연관 검색어를 조회할 검색어",
    )
):
    return []
