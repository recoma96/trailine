from pydantic import BaseModel

from typing import Optional


class PointSchema(BaseModel):
    lat: float
    lon: float
    ele: Optional[float]
