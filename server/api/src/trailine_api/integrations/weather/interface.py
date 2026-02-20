from abc import ABCMeta, abstractmethod
from typing import List
from datetime import datetime

from trailine_api.integrations.external_api import ExternalAPIClient
from trailine_api.integrations.weather.schemas import KmaMountainWeatherItemParsed


class IWeatherProvider(metaclass=ABCMeta):
    client: ExternalAPIClient

    def __init__(self, client: ExternalAPIClient):
        self.client = client

    @abstractmethod
    async def forecast_current(
            self, lat: float, lon: float, target_dt: datetime)  -> List[KmaMountainWeatherItemParsed]:
        pass
