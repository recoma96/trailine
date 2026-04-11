from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Tuple
import collections
import math

import httpx

from trailine_api.common.types import (
    DatagoMiddleForecastSkyCondition,
    DatagoShortForecastRainCondition,
    DatagoShortForecastSkyCondition
)
from trailine_api.schemas.weather import MidLandForecastItem, MidLandTemperatureItem, ShortForecastItem


# ──────────────────────────────────────────
# Base
# ──────────────────────────────────────────

class DatagoAPI:
    service_key: str
    url: str
    base_url: str = "https://apis.data.go.kr"

    def __init__(self, service_key: str, uri: str):
        self.service_key = service_key
        self.url = f"{self.base_url}{uri}"

    @staticmethod
    def _parse_response(response: httpx.Response) -> Dict | None:
        data = response.json()
        result_code = data["response"]["header"]["resultCode"]
        if result_code == "03": # 데이터 없음
            return None
        elif result_code != "00":
            result_msg = data["response"]["header"]["resultMsg"]
            raise ValueError(f"Datago API error: [{result_code}] {result_msg}")
        return data["response"]["body"]["items"]


class KmaMidForecastBase(DatagoAPI):
    """기상청 중기예보 API 공통 베이스 클래스.
    중기예보 API들이 공유하는 요청 로직(시간 변환, API 호출, 응답 파싱)을 제공한다.
    하위 클래스에서 call()과 _parse_items()를 구현하여 사용한다.
    """

    def get_published_at(self) -> datetime:
        """현재 시각 기준 중기예보의 발표 시각을 datetime으로 반환한다."""
        forecast_time_str = self._convert_time_to_forecast_time(datetime.now())
        return datetime.strptime(forecast_time_str, "%Y%m%d%H%M")

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

        res_items = self._parse_response(response)

        if not res_items:
            return {}

        return res_items["item"][0]

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

    @abstractmethod
    def get_published_at(self) -> datetime:
        pass


class IKmaMidLandTemperatureAPI(metaclass=ABCMeta):
    """중기 날씨 기온 예보
    """
    @abstractmethod
    def call(self, regional_code: str) -> List[MidLandTemperatureItem]:
        pass

    @abstractmethod
    def get_published_at(self) -> datetime:
        pass


class IKmaShortForecastAPI(metaclass=ABCMeta):
    """단기 날씨 예보
    """
    @abstractmethod
    def call(self, nx: int, ny: int, days: int) -> List[ShortForecastItem]:
        pass

    @abstractmethod
    def get_published_at(self) -> datetime:
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
                sky_am = DatagoMiddleForecastSkyCondition.from_korean(item[f"wf{day}Am"])
                sky_pm = DatagoMiddleForecastSkyCondition.from_korean(item[f"wf{day}Pm"])
            else:
                rain_am = item[f"rnSt{day}"]
                rain_pm = rain_am
                sky_am = DatagoMiddleForecastSkyCondition.from_korean(item[f"wf{day}"])
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


class KmaShortForecastAPI(DatagoAPI, IKmaShortForecastAPI):
    _BASE_TIMES = ["0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300"]

    def __init__(self, service_key: str):
        super().__init__(service_key, "/1360000/VilageFcstInfoService_2.0/getVilageFcst")

    def get_published_at(self) -> datetime:
        """현재 시각 기준 단기예보의 발표 시각을 datetime으로 반환한다."""
        base_date, base_time = self._convert_time_to_forecast_time(datetime.now())
        return datetime.strptime(f"{base_date}{base_time}", "%Y%m%d%H%M")

    def call(self, nx: int, ny: int, days: int) -> List[ShortForecastItem]:
        if days > 4:
            days = 4

        today = date.today()
        base_date, base_time = self._convert_time_to_forecast_time(datetime.now())

        end_date = today + timedelta(days=days)
        prev_base_date: None | date = None
        page = 1
        raw_items: Dict[datetime, Dict[str, Any]] = collections.defaultdict(dict)

        while True:
            # While문 탈출 여부
            if (
                    prev_base_date is not None
                    and prev_base_date > end_date
            ):
                break

            # API 호출
            response = httpx.get(self.url, params={
                "serviceKey": self.service_key,
                "dataType": "JSON",
                "numOfRows": 500,
                "pageNo": page,
                "base_date": base_date,
                "base_time": base_time,
                "nx": nx,
                "ny": ny,
            })
            response.raise_for_status()

            # 데이터 수집
            res_items: Dict | None = self._parse_response(response)
            if not res_items:
                break

            items = res_items["item"]

            for item in items:
                forecast_date, forecast_time = item["fcstDate"], item["fcstTime"]
                forecast_date_key = datetime.strptime(f"{forecast_date}{forecast_time}", "%Y%m%d%H%M")

                category, value = item["category"], item["fcstValue"]
                prev_base_date = forecast_date_key.date()
                if prev_base_date > end_date:
                    break

                raw_items[forecast_date_key]["forecast_date"] = forecast_date_key

                if category == "POP":
                    raw_items[forecast_date_key]["rain_probability"] = int(value)
                elif category == "PTY":
                    raw_items[forecast_date_key]["rain_condition"] = DatagoShortForecastRainCondition.from_code(int(value))
                elif category == "PCP":
                    raw_items[forecast_date_key]["rain_amount"] = self._parse_precipitation(value)
                elif category == "REH":
                    raw_items[forecast_date_key]["humidity"] = int(value)
                elif category == "SNO":
                    raw_items[forecast_date_key]["snow_amount"] = self._parse_snow(value)
                elif category == "SKY":
                    raw_items[forecast_date_key]["sky_condition"] = DatagoShortForecastSkyCondition.from_code(int(value))
                elif category == "TMP":
                    raw_items[forecast_date_key]["temperature"] = int(value)
                elif category == "TMN":
                    raw_items[forecast_date_key]["min_temperature"] = math.floor(float(value))
                elif category == "TMX":
                    raw_items[forecast_date_key]["max_temperature"] = math.floor(float(value))

            page += 1

        return [
            ShortForecastItem(**data)
            for _, data in sorted(raw_items.items())
        ]

    @staticmethod
    def _parse_precipitation(value: str) -> float:
        if value == "강수없음" or value == "0":
            return 0.0
        if value == "1mm 미만":
            return 0.5
        if value == "50.0mm 이상":
            return 50.0
        return float(value[:-2])

    @staticmethod
    def _parse_snow(value: str) -> float:
        if value == "적설없음" or value == "0":
            return 0.0
        if value == "0.5cm 미만":
            return 0.5
        if value == "5.0cm 이상":
            return 5.0
        return float(value[:-2])

    @staticmethod
    def _convert_time_to_forecast_time(_date: datetime) -> Tuple[str, str]:
        """현재 시각을 단기예보 base_date, base_time으로 변환한다.

        API 제공 시간은 base_time + 10분이므로,
        해당 시각 이전이면 직전 base_time을 사용한다.
        00:00~02:10 사이에는 전날 2300을 사용한다.

        Returns:
            (base_date "YYYYMMDD", base_time "HH00")
        """
        current_minutes = _date.hour * 60 + _date.minute

        # 각 base_time의 API 제공 시각(분): 02:10=130, 05:10=310, ...
        available_minutes = [int(bt[:2]) * 60 + 10 for bt in KmaShortForecastAPI._BASE_TIMES]

        selected_index = -1
        for i, avail in enumerate(available_minutes):
            if current_minutes >= avail:
                selected_index = i

        if selected_index == -1:
            # 00:00 ~ 02:10 -> 전일 2300
            base_time = "2300"
            _date = _date - timedelta(days=1)
        else:
            base_time = KmaShortForecastAPI._BASE_TIMES[selected_index]

        return _date.strftime("%Y%m%d"), base_time
