from typing import List

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import Integer, String, SmallInteger, Text, ForeignKey, CheckConstraint, Boolean, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from trailine_model.base import Base, TimeStampModel
from trailine_model.models.place import Place


class CourseIntervalDifficulty(Base, TimeStampModel):
    __tablename__ = "course_interval_difficulty"
    __table_args__ = {
        "comment": "코스 구간 난이도"
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, comment="난이도 코드명(영어)")
    name: Mapped[str] = mapped_column(String(16), nullable=False, comment="난이도 이름(한글)")
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False, unique=True, comment="난이도 수치(레벨)")
    description: Mapped[str] = mapped_column(Text, nullable=True)


class CourseDifficulty(Base, TimeStampModel):
    __tablename__ = "course_difficulty"
    __table_args__ = {
        "comment": "코스 난이도",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, comment="난이도 코드명(영어)")
    name: Mapped[str] = mapped_column(String(16), nullable=False, comment="난이도 이름(한글)")
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False, unique=True, comment="난이도 수치(레벨)")
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def __str__(self) -> str:
        return f"({self.level}) {self.code} {self.name}"


class CourseInterval(Base, TimeStampModel):
    __tablename__ = "course_interval"
    __table_args__ = (
        CheckConstraint(    # 무향 그래프: (a.id, b.id), (b.id, a.id) 동시 존재 방지
            "place_a_id < place_b_id",
            name="ck_course_interval_undirected_order",
        ),
        {"comment": "코스 구간 (Place 사이를 잇는 간선)"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    geom: Mapped[WKBElement] = mapped_column(Geometry("LINESTRINGZ", srid=4326),
                                             nullable=False, comment="간선 GPX데이터 (위도, 경도, 고도)")

    place_a_id: Mapped[int] = mapped_column(ForeignKey("place.id"), nullable=False, comment="지점A")
    place_b_id: Mapped[int] = mapped_column(ForeignKey("place.id"), nullable=False, comment="지점B")
    course_interval_difficulty_id = mapped_column(ForeignKey("course_interval_difficulty.id"),
                                                  nullable=True, comment="구간 난이도")

    place_a: Mapped[Place] = relationship(foreign_keys=[place_a_id])
    place_b: Mapped[Place] = relationship(foreign_keys=[place_b_id])
    difficulty: Mapped[CourseIntervalDifficulty] = relationship(foreign_keys=[course_interval_difficulty_id])

    courses: Mapped[List["CourseCourseInterval"]] = relationship(
        back_populates="interval",
    )

    def __str__(self) -> str:
        # Admin에서의 Place Lazy Loading 이슈로 인해 이란 Name대신 고유 ID로 임시방편
        # TODO 추후 해당 관련 이슈 해결 필요
        return f"Place A to B: {self.place_a_id} - {self.place_b_id}"


class CourseStyle(Base, TimeStampModel):
    __tablename__ = "course_style"
    __table_args__ = {
        "comment": "코스 형식(스타일)"
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, comment="코드명")
    name: Mapped[str] = mapped_column(String(16), nullable=False, comment="이름(한글)")
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class Course(Base, TimeStampModel):
    __tablename__ = "course"
    __table_args__ = {
        "comment": "코스",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    course_difficulty_id: Mapped[int] = mapped_column(ForeignKey("course_difficulty.id"), nullable=False)
    course_style_id: Mapped[int] = mapped_column(ForeignKey("course_style.id"), nullable=False)

    course_difficulty: Mapped[CourseDifficulty] = relationship(foreign_keys=[course_difficulty_id])
    course_style: Mapped[CourseStyle] = relationship(foreign_keys=[course_style_id])
    _interval_associations: Mapped[List["CourseCourseInterval"]] = relationship(
        order_by="CourseCourseInterval.position",
        back_populates="course",
        cascade="save-update, merge, delete",
        lazy="joined"
    )
    intervals: Mapped[List["CourseInterval"]] = association_proxy(
        "_interval_associations",
        "interval"
    )

    images: Mapped[List["CourseImage"]] = relationship("CourseImage", back_populates="course")

    def __str__(self):
        return f"{self.name}"


class CourseCourseInterval(Base, TimeStampModel):
    __tablename__ = "course_course_interval"
    __table_args__ = (
        UniqueConstraint("course_id", "interval_id", "position", name="course_course_interval_unique"),
        {"comment": "코스 - 구간 사이의 중간 테이블"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
    interval_id: Mapped[int] = mapped_column(ForeignKey("course_interval.id", ondelete="RESTRICT"), nullable=False)
    # Interval을 삭제할 경우 공개된 Course 정보에 손상이 가기 때문에 RESTRICT로 설정
    position: Mapped[int] = mapped_column(Integer, nullable=False, comment="구간 순서")
    is_reversed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"),
                                              comment="구간 역방향 여부 (기본: place_a -> place_b)")

    course: Mapped["Course"] = relationship(back_populates="_interval_associations")
    interval: Mapped["CourseInterval"] = relationship(back_populates="courses")

    def __str__(self):
        direction = "B->A" if self.is_reversed else "A->B"
        return f"<CourseID: {self.course_id} - IntervalID: {self.interval_id} ({direction}) - Pos: {self.position}>"


class CourseImage(Base, TimeStampModel):
    __tablename__ = "course_image"
    __table_args__ = (
        {"comment": "코스 이미지 리스트"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, comment="정렬 순서 (값이 작을 수록 앞에 둔다)")
    url: Mapped[str] = mapped_column(String(256), nullable=False)
    title: Mapped[str] = mapped_column(String(32), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id", onupdate="CASCADE", ondelete="SET NULL"),
                                           nullable=True)

    course: Mapped[Course] = relationship("Course", back_populates="images")
