from abc import ABCMeta, abstractmethod
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from trailine_model.models.course import Course
from trailine_model.models.forecast import KmaMidLandStatusArea, KmaMidLandTempArea


class IWeatherRepository(metaclass=ABCMeta):
    @abstractmethod
    def get_mid_land_forecast_codes(
        self, session: Session, course_id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        특정 코스에 대한 중기육상예보 지역 코드를 가져오는 함수

        :param session: DB session
        :param course_id: 코스 아이디
        :return: (status_code, temp_code) -> (날씨 지역코드, 온도 지역코드), 미설정 시 None
        :raises ValueError: course_id에 해당하는 코스가 없을 때
        """
        pass


class WeatherRepository(IWeatherRepository):
    def get_mid_land_forecast_codes(
        self, session: Session, course_id: int
    ) -> Tuple[Optional[str], Optional[str]]:
        stmt = (
            select(
                KmaMidLandStatusArea.code.label("status_code"),
                KmaMidLandTempArea.code.label("temp_code"),
            )
            .select_from(Course)
            .outerjoin(KmaMidLandStatusArea, Course.kma_mid_land_status_area_id == KmaMidLandStatusArea.id)
            .outerjoin(KmaMidLandTempArea, Course.kma_mid_land_temp_area_id == KmaMidLandTempArea.id)
            .where(Course.id == course_id)
        )

        row = session.execute(stmt).one_or_none()
        if row is None:
            raise ValueError(f"Course not found: {course_id}")

        return row.status_code, row.temp_code
