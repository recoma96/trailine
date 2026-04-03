from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx

from trailine_api.common.types import DataGoMiddleForecastSkyCondition
from trailine_api.schemas.weather import MidLandForecastItem, MidLandTemperatureItem


# ──────────────────────────────────────────
# Base
# ──────────────────────────────────────────

class DatagoAPI:
    service_key: str
    url: str
    base_url: str = "http://apis.data.go.kr"

    def __init__(self, service_key: str, uri: str):
        self.service_key = service_key
        self.url = f"{self.base_url}{uri}"

    @staticmethod
    def _parse_response(response: httpx.Response) -> Dict:
        data = response.json()
        result_code = data["response"]["header"]["resultCode"]
        if result_code != "00":
            result_msg = data["response"]["header"]["resultMsg"]
            raise ValueError(f"Datago API error: [{result_code}] {result_msg}")
        return data["response"]["body"]["items"]


class KmaMidForecastBase(DatagoAPI):
    """기상청 중기예보 API 공통 베이스 클래스.
    중기예보 API들이 공유하는 요청 로직(시간 변환, API 호출, 응답 파싱)을 제공한다.
    하위 클래스에서 call()과 _parse_items()를 구현하여 사용한다.
    """

    def _fetch_first_item(self, regional_code: str) -> Dict[str, Any]:
        """정상 응답 시, 실제 데이터 추출
        """
        forecast_time = self._convert_time_to_forecast_time(datetime.now())
        response = httpx.get(self.url, params={
            "serviceKey": self.service_key,
            "dataType": "JSON",
            "regId": regional_code,
            "tmFc": forecast_time,
        })
        response.raise_for_status()
        return self._parse_response(response)["item"][0]

    @staticmethod
    def _convert_time_to_forecast_time(_date: datetime) -> str:
        """시간을 중기 예보에 맞게 수정

        if 0 <= hour < 6
            then 어제자 18시
        elif 6 <= hour < 18
            then 오늘자 6시
        else
            then 오늘자 18시
        """
        if _date.hour < 6:
            base = _date - timedelta(days=1)
            base = base.replace(hour=18, minute=0, second=0, microsecond=0)
        elif _date.hour < 18:
            base = _date.replace(hour=6, minute=0, second=0, microsecond=0)
        else:
            base = _date.replace(hour=18, minute=0, second=0, microsecond=0)

        return f"{base.year}{base.month:02d}{base.day:02d}{base.hour:02d}00"


# ──────────────────────────────────────────
# Interface
# ──────────────────────────────────────────

class IKmaMidLandForecastAPI(metaclass=ABCMeta):
    """중기 날씨 상태 예보
    """
    @abstractmethod
    def call(self, regional_code: str) -> List[MidLandForecastItem]:
        pass


class IKmaMidLandTemperatureAPI(metaclass=ABCMeta):
    """중기 날씨 기온 예보
    """
    @abstractmethod
    def call(self, regional_code: str) -> List[MidLandTemperatureItem]:
        pass


# ──────────────────────────────────────────
# Implementation
# ──────────────────────────────────────────

class KmaMidLandForecastAPI(KmaMidForecastBase, IKmaMidLandForecastAPI):
    def __init__(self, service_key: str):
        super().__init__(service_key, "/1360000/MidFcstInfoService/getMidLandFcst")

    def call(self, regional_code: str) -> List[MidLandForecastItem]:
        return self._parse_items(self._fetch_first_item(regional_code))

    @staticmethod
    def _parse_items(item: Dict[str, Any]) -> List[MidLandForecastItem]:
        results: List[MidLandForecastItem] = []
        for day in range(5, 11):
            if day <= 7:
                rain_am = item[f"rnSt{day}Am"]
                rain_pm = item[f"rnSt{day}Pm"]
                sky_am = DataGoMiddleForecastSkyCondition.from_korean(item[f"wf{day}Am"])
                sky_pm = DataGoMiddleForecastSkyCondition.from_korean(item[f"wf{day}Pm"])
            else:
                rain_am = item[f"rnSt{day}"]
                rain_pm = rain_am
                sky_am = DataGoMiddleForecastSkyCondition.from_korean(item[f"wf{day}"])
                sky_pm = sky_am

            results.append(MidLandForecastItem(
                rain_probability_am=rain_am,
                rain_probability_pm=rain_pm,
                sky_condition_am=sky_am,
                sky_condition_pm=sky_pm,
            ))
        return results



class KmaMidLandTemperatureAPI(KmaMidForecastBase, IKmaMidLandTemperatureAPI):
    def __init__(self, service_key: str):
        super().__init__(service_key, "/1360000/MidFcstInfoService/getMidTa")

    def call(self, regional_code: str) -> List[MidLandTemperatureItem]:
        return self._parse_items(self._fetch_first_item(regional_code))

    @staticmethod
    def _parse_items(item: Dict[str, Any]) -> List[MidLandTemperatureItem]:
        results: List[MidLandTemperatureItem] = []
        for day in range(5, 11):
            results.append(MidLandTemperatureItem(
                min_temperature=item[f"taMin{day}"],
                max_temperature=item[f"taMax{day}"],
            ))
        return results
