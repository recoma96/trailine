from typing import Optional

from pydantic import BaseModel, Field


class PlaceSchema(BaseModel):
    id: int
    name: str
    land_address: Optional[str] = Field(..., alias="landAddress", description="지번주소")
    road_address: Optional[str] = Field(..., alias="roadAddress", description="도로명주소")
    lat: Optional[float] = Field(..., description="위도")
    lon: Optional[float] = Field(..., description="경도")
    ele: Optional[float] = Field(..., description="해발고도")
