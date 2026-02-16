from typing import Any

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry, Geography


from trailine_model.base import Base, TimeStampModel


class KmaMountainWeatherArea(Base, TimeStampModel):
    __tablename__ = "kma_mountain_weather_area"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, comment="기상청 산악예보 식별번호")
    name: Mapped[str] = mapped_column(String(16), nullable=False, comment="산악지형 이름")
    geom: Mapped[Any] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False,
                                      comment="위경도(뷰포트 검색용)")
    geog: Mapped[Any] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False,
                                      comment="위경도(거리, 버퍼 연산)")
    elevation: Mapped[int] = mapped_column(Integer, nullable=False, comment="해발고도 (m)")
