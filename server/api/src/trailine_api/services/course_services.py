from abc import ABCMeta, abstractmethod
from typing import Optional, List, cast, Tuple, Dict

from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from trailine_api.repositories.course_repositories import (
    ICourseRepository,
    ICourseDifficultyRepository,
    ICourseStyleRepository
)
from trailine_api.repositories.place_repositories import IPlaceRepository
from trailine_api.schemas.course import (
    CourseSearchSchema,
    CourseDifficultySchema,
    CourseStyleSchema,
    CourseDetailSchema,
    CourseImageSchema,
    CourseIntervalSchema,
    CourseIntervalImageSchema,
    CourseIntervalDifficultySchema
)
from trailine_api.schemas.place import PlaceSchema
from trailine_api.schemas.point import PointSchema
from trailine_model.base import SessionLocal
from trailine_model.models.place import Place
from trailine_model.models.course import CourseInterval


class ICourseService(metaclass=ABCMeta):
    _course_repository: ICourseRepository
    _course_difficulty_repository: ICourseDifficultyRepository
    _course_style_repository: ICourseStyleRepository
    _place_repository: IPlaceRepository

    def __init__(
            self,
            course_repository: ICourseRepository,
            place_repository: IPlaceRepository,
            course_difficulty_repository: ICourseDifficultyRepository,
            course_style_repository: ICourseStyleRepository
    ):
        self._course_repository = course_repository
        self._place_repository = place_repository
        self._course_difficulty_repository = course_difficulty_repository
        self._course_style_repository = course_style_repository

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

    @abstractmethod
    def get_course_detail(self, course_id: int) -> Optional[CourseDetailSchema]:
        pass

    @abstractmethod
    def get_course_intervals(self, course_id: int) -> Optional[List[CourseIntervalSchema]]:
        pass

    @abstractmethod
    def get_course_difficulty_list(self) -> List[CourseDifficultySchema]:
        pass

    @abstractmethod
    def get_course_style_list(self) -> List[CourseStyleSchema]:
        pass


class CourseService(ICourseService):
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
                        name=row["difficulty_name"],
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

    def get_course_detail(self, course_id: int) -> Optional[CourseDetailSchema]:
        with (SessionLocal() as session, session.begin()):
            raw_result = self._course_repository.get_course_detail(session, course_id)

        if raw_result is None:
            return None

        course_detail = CourseDetailSchema(
            id=raw_result["id"],
            name=raw_result["name"],
            description=raw_result["description"],
            loadAddresses=raw_result["road_addresses"],
            roadAddresses=raw_result["land_addresses"],
            difficulty=CourseDifficultySchema(**raw_result["difficulty"]),
            courseStyle=CourseStyleSchema(**raw_result["course_style"]),
            images=[
                CourseImageSchema(**image)
                for image in raw_result["images"]
            ]
        )

        return course_detail

    def get_course_intervals(self, course_id: int) -> Optional[List[CourseIntervalSchema]]:
        interval_schemas: List[CourseIntervalSchema] = []
        with (SessionLocal() as session, session.begin()):
            # 구간 데이터 및 역방향 여부 가져오기
            intervals, is_reversed_list = self._course_repository.get_intervals(session, course_id)
            if not intervals:
                return None

            for i, interval in enumerate(intervals):
                # 시작지점, 마감지점 가져오기
                start_place, end_place = self._get_start_and_end_place(session, interval, is_reversed_list[i])
                start_place_location = self._get_location_from_place(start_place)
                end_place_location = self._get_location_from_place(end_place)
                track_points = self._get_points(interval, is_reversed_list[i])

                interval_schemas.append(CourseIntervalSchema(
                    name=interval.name,
                    description=interval.description,
                    images=[
                        CourseIntervalImageSchema(
                            title=image.title,
                            description=image.description,
                            url=image.url
                        )
                        for image in interval.images
                    ],
                    difficulty=CourseIntervalDifficultySchema(
                        id=interval.difficulty.id,
                        code=interval.difficulty.code,
                        name=interval.difficulty.name,
                        level=interval.difficulty.level,
                    ),
                    startPlace=PlaceSchema(
                        id=start_place.id,
                        name=start_place.name,
                        landAddress=start_place.land_address,
                        roadAddress=start_place.road_address,
                        lat=start_place_location["lat"],
                        lon=start_place_location["lon"],
                        ele=start_place_location["ele"],
                    ),
                    endPlace=PlaceSchema(
                        id=end_place.id,
                        name=end_place.name,
                        landAddress=end_place.land_address,
                        roadAddress=end_place.road_address,
                        lat=end_place_location["lat"],
                        lon=end_place_location["lon"],
                        ele=end_place_location["ele"],
                    ),
                    points=[
                        PointSchema(lat=p["lat"], lon=p["lon"], ele=p["ele"])
                        for p in track_points
                    ]
                ))

        return interval_schemas

    def _get_start_and_end_place(
            self,
            session: Session,
            interval: CourseInterval,
            is_reversed: bool
    ) -> Tuple[Place, Place]:
        start_place_id = interval.place_a_id if not is_reversed else interval.place_b_id
        end_place_id = interval.place_b_id if start_place_id == interval.place_a_id else interval.place_a_id

        start_place = self._place_repository.get_place_by_instance(session, start_place_id)
        if not start_place:
            raise ValueError("Start Place Not Found")

        end_place = self._place_repository.get_place_by_instance(session, end_place_id)
        if not end_place:
            raise ValueError("End Place Not Found")

        return start_place, end_place

    def _get_location_from_place(self, place: Place) -> Dict[str, Optional[float]]:
        shape = to_shape(place.geom)

        location = {
            "lat": shape.y,
            "lon": shape.x,
            "ele": shape.z if shape.has_z else None
        }

        return location

    def _get_points(self, interval: CourseInterval, is_reverse: bool) -> List[Dict[str, float]]:
        shape = to_shape(interval.geom)

        track_points: List[Dict[str, float]] = []
        """ DB 상에서 해발고도(z)는 무조건 존재함을 보장하기 때문에 따로 분기처리할 필요가 없다.
        if shape.has_z:
            for lon, lat, ele in shape.coords:
                track_points.append({"lat": lat, "lon": lon, "ele": ele})
        """
        for lon, lat, ele in shape.coords:
            track_points.append({"lat": lat, "lon": lon, "ele": ele})

        if is_reverse:
            track_points.reverse()

        return track_points

    def get_course_difficulty_list(self) -> List[CourseDifficultySchema]:
        with (SessionLocal() as session, session.begin()):
            instances = self._course_difficulty_repository.get_course_difficulty_all(session)
            return [
                CourseDifficultySchema(
                    id=instance.id,
                    code=instance.code,
                    name=instance.name,
                    level=instance.level,
                )
                for instance in instances
            ]

    def get_course_style_list(self) -> List[CourseStyleSchema]:
        with (SessionLocal() as session, session.begin()):
            instances = self._course_style_repository.get_course_style_all(session)
            return [
                CourseStyleSchema(
                    id=instance.id,
                    code=instance.code,
                    name=instance.name,
                )
                for instance in instances
            ]
