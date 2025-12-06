from abc import ABCMeta, abstractmethod
from typing import Optional, Sequence, List

from sqlalchemy import select, or_, func, cast, Integer, values, literal, literal_column
from sqlalchemy.orm import Session, aliased

from trailine_api.common.types import SQLRowList, SQLRow
from trailine_model.models.place import Place
from trailine_model.models.course import (
    Course,
    CourseCourseInterval,
    CourseInterval,
    CourseDifficulty,
    CourseStyle,
    CourseImage,
)


class ICourseRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_course_ids_by_search(
            self,
            session: Session,
            word: Optional[str],
            difficulties: Optional[List[int]],
            course_styles: Optional[List[int]],
            page: int,
            page_size: int
    ) -> Sequence[int]:
        pass

    @abstractmethod
    def get_course_list_information(self, session: Session, course_id_list: Sequence[int]) -> SQLRowList:
        """
        검색된 코스 아이디에 대해 리스트 조회에 필요한 정볼르 Dict형태로 가져오는 함수
        """
        pass

    @abstractmethod
    def get_course_detail(self, session: Session, course_id: int) -> Optional[SQLRow]:
        """
        코스 상세 정보
        """
        pass


class CourseRepository(ICourseRepository):
    def get_course_ids_by_search(
            self,
            session: Session,
            word: Optional[str],
            difficulties: Optional[List[int]],
            course_styles: Optional[List[int]],
            page: int,
            page_size: int
    ) -> Sequence[int]:
        # place_a, place_b를 조인하기 위해 별칭(alias)을 사용합니다.
        place_a, place_b = aliased(Place), aliased(Place)

        stmt = (
            select(Course.id)
            .join(CourseCourseInterval, CourseCourseInterval.course_id == Course.id)
            .join(CourseInterval, CourseInterval.id == CourseCourseInterval.interval_id)
            .join(place_a, CourseInterval.place_a_id == place_a.id)  # p1
            .join(place_b, CourseInterval.place_b_id == place_b.id)  # p2
        )

        word_s: str = f"%{word}%" if word else ""
        if word:
            stmt = stmt.where(
                or_(
                    Course.name.like(word_s),
                    place_a.land_address.like(word_s),
                    place_b.land_address.like(word_s),
                    place_a.road_address.like(word_s),
                    place_b.road_address.like(word_s)
                )
            )
        if difficulties:
            stmt = stmt.where(Course.course_difficulty_id.in_(difficulties))
        if course_styles:
            stmt = stmt.where(Course.course_style_id.in_(course_styles))

        # Course.id로 그룹화하고, 정렬 및 페이지네이션을 적용합니다.
        stmt = (
            stmt.group_by(Course.id)
            .order_by(
                # Course.name이 일치하는 경우를 우선 정렬합니다.
                func.max(cast(Course.name.like(word_s), Integer)).desc(),
                Course.id  # 2차 정렬
            )
            .limit(page_size)
            .offset((page - 1) * page_size)
        )

        course_id_list: Sequence[int] = session.scalars(stmt).all()
        return course_id_list

    def _build_course_information_query(self):
        """
        코스 리스트와 상세 정보 조회에 사용되는 공통 쿼리를 생성하는 헬퍼 메서드
        """
        place_a, place_b = aliased(Place), aliased(Place)

        # corss join literal ... land_address
        land_addr = values(
            literal_column("land_addrs")
        ).data(
            [(place_a.land_address,), (place_b.land_address,)]
        ).lateral("land_addr")

        # cross join literal ... road_address
        road_addr = values(
            literal_column("road_addrs")
        ).data(
            [(place_a.road_address,), (place_b.road_address,)]
        ).lateral("road_addr")

        # Main Query
        stmt = (
            select(
                Course.id.label("id"),
                Course.name.label("name"),
                CourseDifficulty.id.label("difficulty_id"),
                CourseDifficulty.level.label("difficulty_level"),
                CourseDifficulty.code.label("difficulty_code"),
                CourseStyle.id.label("course_style_id"),
                CourseStyle.code.label("course_style_label"),
                CourseStyle.name.label("course_style_name"),
                land_addr.c.land_addrs.label("land_addresses"),
                road_addr.c.road_addrs.label("road_addresses"),
            )
            .join(CourseCourseInterval, Course.id == CourseCourseInterval.course_id)
            .join(CourseInterval, CourseCourseInterval.interval_id == CourseInterval.id)
            .join(CourseDifficulty, Course.course_difficulty_id == CourseDifficulty.id)
            .join(CourseStyle, Course.course_style_id == CourseStyle.id)
            .join(place_a, CourseInterval.place_a_id == place_a.id)
            .join(place_b, CourseInterval.place_b_id == place_b.id)
            .join(land_addr, literal(True))
            .join(road_addr, literal(True))
            .where(
                Course.is_published.is_(True),
                land_addr.c.land_addrs.is_not(None),
                road_addr.c.road_addrs.is_not(None)
            )
        )
        return stmt

    def get_course_list_information(self, session: Session, course_id_list: Sequence[int]) -> SQLRowList:
        base_stmt = self._build_course_information_query()
        stmt = base_stmt.where(Course.id.in_(course_id_list))
        results = [dict(row) for row in session.execute(stmt).mappings()]
        return results

    def get_course_images(self, session: Session, course_id: int) -> Sequence[CourseImage]:
        stmt = (
            select(CourseImage)
            .where(CourseImage.course_id == course_id)
            .order_by(CourseImage.sort_order)
        )
        result = session.execute(stmt).scalars().all()
        return result

    def get_course_detail(self, session: Session, course_id: int) -> Optional[SQLRow]:
        base_stmt = self._build_course_information_query().add_columns(
            Course.description.label("description"),
        )
        stmt = (
            base_stmt
            .where(Course.id == course_id)
        )

        rows = session.execute(stmt).mappings().all()
        if not rows:
            return None

        # Dict화
        data: SQLRow = {
            "id": rows[0]["id"],
            "name": rows[0]["name"],
            "description": rows[0]["description"],
            "land_addresses": list({row["land_addresses"] for row in rows}),
            "road_addresses": list({row["road_addresses"] for row in rows}),
            "difficulty": {
                "id": rows[0]["difficulty_id"],
                "code": rows[0]["difficulty_code"],
                "level": rows[0]["difficulty_level"],
            },
            "course_style": {
                "id": rows[0]["course_style_id"],
                "code": rows[0]["course_style_label"],
                "name": rows[0]["course_style_name"],
            },
            "images": [
                {"title": img.title, "description": img.description, "url": img.url}
                for img in self.get_course_images(session, course_id)
            ],
        }

        return data
