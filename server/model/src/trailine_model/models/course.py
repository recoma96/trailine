from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer, String, SmallInteger, Text, ForeignKey, CheckConstraint
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
