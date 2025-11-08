from sqlalchemy import Integer, String, SmallInteger, Text
from sqlalchemy.orm import Mapped, mapped_column

from trailine_model.base import Base, TimeStampModel


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
