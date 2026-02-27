from abc import ABCMeta, abstractmethod
from typing import List
from datetime import datetime

from trailine_api.integrations.external_api import ExternalAPIClient


class IWeatherProvider(metaclass=ABCMeta):
    client: ExternalAPIClient

    def __init__(self, client: ExternalAPIClient):
        self.client = client

    @abstractmethod
    async def get_current_weather(
            self, lat: float, lon: float, target_dt: datetime)  -> List:
        pass
