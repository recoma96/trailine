from abc import ABCMeta, abstractmethod
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint

from trailine_model.models.weather import KmaMountainWeatherArea


class IWeatherRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_nearest_mountain_area_code(self, session: Session, lat: float, lon: float) -> Optional[int]:
        pass


class WeatherRepository(IWeatherRepository):
    def get_nearest_mountain_area_code(self, session: Session, lat: float, lon: float) -> Optional[int]:
        """
        주어진 위경도와 가장 가까운 산악 기상 구역의 코드를 반환합니다.
        """
        # PostGIS의 <-> 연산자를 사용하여 가장 가까운 지점을 효율적으로 찾습니다.
        # model 정의에서 geog가 Geometry(POINT, 4326)으로 되어 있으므로 이를 활용합니다.
        point = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
        
        # 참고: distance_centroid는 <-> 연산자에 대응하는 GeoAlchemy2의 함수입니다.
        # 만약 정확한 거리순 정렬이 필요하다면 ST_Distance를 사용할 수 있으나, 
        # 가장 가까운 점 하나를 찾는 데는 인덱스를 타는 <-> (<->) 연산자가 유리합니다.
        # 여기서는 GeoAlchemy2의 distance_centroid 또는 distance_box를 검토해야 함.
        stmt = (
            select(KmaMountainWeatherArea.code)
            .order_by(KmaMountainWeatherArea.geog.distance_centroid(point))
            .limit(1)
        )
        
        return session.execute(stmt).scalar()
