from typing import Optional

from pydantic import BaseModel, Field


class PlaceSchema(BaseModel):
    id: int
    name: str
    land_address: Optional[str]
    road_address: Optional[str]
    lat: float = Field(..., description="위도")
    lng: float = Field(..., description="경도")
    ele: Optional[float] = Field(..., description="해발고도")
