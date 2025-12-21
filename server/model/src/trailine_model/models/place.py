from typing import Any

from sqlalchemy import text, Integer, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    elevation: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="해발고도(m)")
    land_address: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="지번 주소")
    road_address: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="도로명 주소")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="설명")
    is_searchable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"), comment="검색 가능 여부")

    images: Mapped[list["PlaceImage"]] = relationship("PlaceImage", back_populates="place")

    def __str__(self) -> str:
        return f"{self.id} - {self.name}"


class PlaceImage(Base, TimeStampModel):
    __tablename__ = "place_image"
    __table_args__ = (
        UniqueConstraint("place_id", "sort_order", name="uq_place_image_place_id_sort_order"),
        {"comment": "장소 이미지 리스트"},
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, comment="정렬 순서 (값이 작을수록 앞에 온다)")
    place_id: Mapped[int | None] = mapped_column(ForeignKey("place.id", onupdate="CASCADE", ondelete="SET NULL"),
                                                 nullable=True, comment="장소 ID")
    url: Mapped[str] = mapped_column(String(256), nullable=False, comment="이미지 전체 URL")
    title: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="이미지 제목")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="이미지 설명")

    place: Mapped["Place"] = relationship("Place", back_populates="images")
