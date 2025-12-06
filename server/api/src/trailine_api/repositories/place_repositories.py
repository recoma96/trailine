from abc import ABCMeta, abstractmethod
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from trailine_model.models.place import Place


class IPlaceRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_place_by_instance(self, session: Session, place_id: int) -> Optional[Place]:
        pass


class PlaceRepository(IPlaceRepository):
    def get_place_by_instance(self, session: Session, place_id: int) -> Optional[Place]:
        stmt = select(Place).filter(Place.id == place_id)
        return session.execute(stmt).scalar_one_or_none()
