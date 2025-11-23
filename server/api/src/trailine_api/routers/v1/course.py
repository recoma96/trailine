from typing import List, Annotated, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Query
from fastapi import status
from fastapi.params import Depends

from trailine_api.container import Container
from trailine_api.schemas.course import CourseSearchResponseSchema
from trailine_api.services.course_services import ICourseServices


router = APIRouter()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="연관 검색어 조회",
    response_model=CourseSearchResponseSchema,
)
@inject
async def get_courses(
    course_service: Annotated[ICourseServices, Depends(Provide[Container.course_services])],
    word: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        title="검색어 (코스명 또는 주소)",
        description="연관 검색어를 조회할 검색어",
    ),
    difficulty: Optional[List[int]] = Query(
        None,
        description="난이도 식별아이디",
    ),
    course_style: Optional[List[int]] = Query(
        None,
        alias="courseStyle",
        description="코스 스타일 식별아이디",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
):
    courses = course_service.get_courses(
        word,
        difficulty,
        course_style,
        page,
        page_size
    )
    return CourseSearchResponseSchema(
        page=page,
        pageSize=page_size,
        total=len(courses),
        courses=courses,
    )
