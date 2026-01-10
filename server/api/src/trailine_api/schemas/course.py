from typing import List, Optional
from pydantic import BaseModel, Field

from trailine_api.schemas.place import PlaceSchema
from trailine_api.schemas.point import PointSchema


class CourseDifficultySchema(BaseModel):
    id: int = Field(..., description="코스난이도 식별자")
    code: str = Field(..., description="난이도 고유코드(영문명)")
    name: str = Field(..., description="난이도 이름(한글명)")
    level: int = Field(..., description="난이도 수치(또는 레벨)")


class CourseStyleSchema(BaseModel):
    id: int = Field(..., description="코스스타일 식별자")
    code: str = Field(..., description="코스스타일 코드명")
    name: str = Field(..., description="코스스타일 이름 (한글명)")


class CourseImageSchema(BaseModel):
    title: Optional[str] = Field(..., description="이미지 제목")
    description: Optional[str] = Field(..., description="이미지 설명")
    url: str = Field(..., description="이미지 URL")


class CourseSearchSchema(BaseModel):
    id: int = Field(..., description="코스 식별자")
    name: str = Field(..., description="코스 난이도")
    load_addresses: List[str] = Field(..., alias="loadAddresses", description="코스에 해당하는 모든 위치(Place)의 도로명 주소 (중복제외)")
    road_addresses: List[str] = Field(..., alias="roadAddresses", description="코스에 해당하는 모든 위치(Place)의 지번 주소 (중복제외)")
    difficulty: CourseDifficultySchema = Field(..., description="코스 난이도 정보")
    course_style: CourseStyleSchema = Field(..., alias="courseStyle", description="코스 스타일")


class CourseSearchResponseSchema(BaseModel):
    page: int = Field(..., description="페이지 번호 (1번부터 시작)")
    page_size: int = Field(..., alias="pageSize", description="페이지 크기 (검색 개수)")
    total: int = Field(..., description="전체 검색 개수")
    total_pages: int = Field(..., alias="totalPages", description="전체 페이지 개수")
    courses: List[CourseSearchSchema] = Field(..., description="검색된 코스")


class CourseDetailSchema(BaseModel):
    id: int = Field(..., description="코스 식별자")
    name: str = Field(..., description="코스 난이도")
    description: Optional[str] = Field(..., description="코스 설명")
    load_addresses: List[str] = Field(..., alias="loadAddresses", description="코스에 해당하는 모든 위치(Place)의 도로명 주소 (중복제외)")
    road_addresses: List[str] = Field(..., alias="roadAddresses", description="코스에 해당하는 모든 위치(Place)의 지번 주소 (중복제외)")
    difficulty: CourseDifficultySchema = Field(..., description="코스 난이도 정보")
    course_style: CourseStyleSchema = Field(..., alias="courseStyle", description="코스 스타일")
    images: List[CourseImageSchema] = Field(..., description="코스 이미지 리스트 (sort_order 오름차순으로 정렬)")
    length: float = Field(..., description="코스 길이 (km단위, 소수 첫째자리 까지만 출력)")
    duration: int = Field(..., description="소요시간 합 (분단위)")


class CourseIntervalImageSchema(BaseModel):
    title: Optional[str] = Field(..., description="이미지 제목")
    description: Optional[str] = Field(..., description="이미지 설명")
    url: str = Field(..., description="이미지 URL")


class CourseIntervalDifficultySchema(BaseModel):
    id: int = Field(..., description="난이도 고유아이디")
    code: str = Field(..., description="난이도 고유 코드 (혹은 영문명)")
    name: str = Field(..., description="난이도 이름 (한글명)")
    level: int = Field(..., description="난이도 수치")


class CourseIntervalSchema(BaseModel):
    name: str = Field(..., description="구간명")
    description: Optional[str] = Field(..., description="설명")
    images: List[CourseIntervalImageSchema] = Field(..., description="이미지 리스트 (sort_order 오름차순으로 정렬)")
    difficulty: CourseIntervalDifficultySchema = Field(..., description="난이도 정보")
    start_place: PlaceSchema = Field(...,alias="startPlace", description="시작지점")
    end_place: PlaceSchema = Field(..., alias="endPlace", description="종료지점")
    points: List[PointSchema] = Field(..., description="포인트(위경도) 경로")


class GettingCourseIntervalResponseSchema(BaseModel):
    interval_count: int = Field(..., alias="intervalCount", description="구간 수")
    intervals: List[CourseIntervalSchema] = Field(..., description="구간들 (순서대로)")
