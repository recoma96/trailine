from abc import ABCMeta, abstractmethod
from typing import Optional, List, cast

from trailine_api.repositories.course_repositories import ICourseRepository
from trailine_api.schemas.course import CourseSearchSchema, CourseDifficultySchema, CourseStyleSchema
from trailine_model.base import SessionLocal


class ICourseServices(metaclass=ABCMeta):
    def __init__(self, course_repository: ICourseRepository):
        self._course_repository = course_repository

    @abstractmethod
    def get_courses(
            self,
            word: Optional[str],
            difficulties: Optional[List[int]],
            course_styles: Optional[List[int]],
            page: int,
            page_size: int
    ) -> List[CourseSearchSchema]:
        pass


class CourseServices(ICourseServices):
    def get_courses(
            self,
            word: Optional[str],
            difficulties: Optional[List[int]],
            course_styles: Optional[List[int]],
            page: int,
            page_size: int
    ) -> List[CourseSearchSchema]:
        with (SessionLocal() as session, session.begin()):
            course_id_list = self._course_repository.get_course_ids_by_search(
                session, word, difficulties, course_styles, page, page_size
            )
            data_size = len(course_id_list)
            result_index_map = {
                course_id: idx
                for idx, course_id in enumerate(course_id_list)
            }

            # 조회된 코스 고유 아이디에 대해 데이터 가져오기
            raw_result = self._course_repository.get_course_list_information(session, course_id_list)

        # CourseSearchSchema 리스트로 포매팅 및 정렬
        # 1. 최종 결과를 담을 리스트를 course_id_list 크기만큼 None으로 초기화
        formatted_results: List[Optional[CourseSearchSchema]] = [None] * data_size

        # 2. raw_result를 순회하며 데이터 가공
        for row in raw_result:
            course_id = row["id"]
            # 3. result_index_map을 사용해 현재 코스가 위치할 인덱스를 찾음
            idx = result_index_map[course_id]
            # 4. 해당 인덱스에 객체가 없으면 새로 생성
            if formatted_results[idx] is None:
                formatted_results[idx] = CourseSearchSchema(
                    id=row["id"],
                    name=row["name"],
                    loadAddress=[row["road_addresses"]],
                    roadAddress=[row["land_addresses"]],
                    difficulty=CourseDifficultySchema(
                        id=row["difficulty_id"],
                        level=row["difficulty_level"],
                        code=row["difficulty_code"],
                    ),
                    courseStyle=CourseStyleSchema(
                        id=row["course_style_id"],
                        code=row["course_style_label"],
                        name=row["course_style_name"],
                    )
                )
            # 5. 이미 객체가 있으면 주소만 추가
            else:
                course = cast(CourseSearchSchema, formatted_results[idx])
                if row["road_addresses"] not in course.load_addresses:
                    course.load_addresses.append(row["road_addresses"])
                if row["land_addresses"] not in course.road_addresses:
                    course.road_addresses.append(row["land_addresses"])

        # 6. 주소 리스트를 정렬하여 일관된 순서 보장
        for item in formatted_results:
            if item:
                item.load_addresses.sort()
                item.road_addresses.sort()

        return [item for item in formatted_results if item is not None]
