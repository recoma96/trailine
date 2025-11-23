from typing import List, Optional
from pydantic import BaseModel, Field


class CourseDifficultySchema(BaseModel):
    id: int = Field(..., description="코스난이도 식별자")
    code: str = Field(..., description="난이도 고유코드(영문명)")
    level: int = Field(..., description="난이도 수치(또는 레벨)")


class CourseStyleSchema(BaseModel):
    id: int = Field(..., description="코스스타일 식별자")
    code: str = Field(..., description="코스스타일 코드명")
    name: str = Field(..., description="코스스타일 이름 (한글명)")


class CourseSearchSchema(BaseModel):
    id: int = Field(..., description="코스 식별자")
    name: str = Field(..., description="코스 난이도")
    load_addresses: List[str] = Field(..., alias="loadAddress", description="코스에 해당하는 모든 위치(Place)의 도로명 주소 (중복제외)")
    road_addresses: List[str] = Field(..., alias="roadAddress", description="코스에 해당하는 모든 위치(Place)의 지번 주소 (중복제외)")
    difficulty: CourseDifficultySchema = Field(..., description="코스 난이도 정보")
    course_style: CourseStyleSchema = Field(..., alias="courseStyle", description="코스 스타일")


class CourseSearchResponseSchema(BaseModel):
    page: int = Field(..., description="페이지 번호 (1번부터 시작)")
    page_size: int = Field(..., alias="pageSize", description="페이지 크기 (검색 개수)")
    total: int = Field(..., description="전체 검색 개수")
    courses: List[CourseSearchSchema] = Field(..., description="검색된 코스")
