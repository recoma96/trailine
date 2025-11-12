from typing import Any

from sqlalchemy import text, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry, Geography

from trailine_model.base import Base, TimeStampModel


class Place(Base, TimeStampModel):
    __tablename__ = "place"
    __table_args__ = {
        "comment": "장소"
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(16), nullable=False)
    geom: Mapped[Any] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False,
                                      comment="위경도(뷰포트 검색용)")
    geog: Mapped[Any] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False,
                                      comment="위경도(거리, 버퍼 연산)")
    elevation: Mapped[int] = mapped_column(Integer, nullable=True, comment="해발고도(m)")
    land_address: Mapped[str] = mapped_column(String(128), nullable=True, comment="지번 주소")
    road_address: Mapped[str] = mapped_column(String(128), nullable=True, comment="도로명 주소")
    description: Mapped[str] = mapped_column(Text, nullable=True, comment="설명")
    is_searchable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"), comment="검색 가능 여부")
