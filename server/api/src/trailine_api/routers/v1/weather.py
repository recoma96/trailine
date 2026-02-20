from typing import Optional, Annotated
from datetime import datetime

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Query, status, Depends

from trailine_api.container import Container
from trailine_api.schemas.weather import CurrentWeatherResponse
from trailine_api.services.weather_services import IWeatherService

router = APIRouter()


@router.get(
    "/current",
    status_code=status.HTTP_200_OK,
    summary="실시간 날씨 조회 (0시간 ~ 3시간)",
    response_model=CurrentWeatherResponse
)
@inject
async def get_weather_current(
    weather_service: Annotated[IWeatherService, Depends(Provide[Container.weather_service])],
    lat: float = Query(..., description="위도"),
    lon: float = Query(..., description="경도"),
    is_mountain: bool = Query(
        True,
        alias="isMountain",
        description="산악지형 기준 날씨조회를 할 때 사용"
    ),
    target_dt_str: Optional[str] = Query(
        None,
        alias="datetime",
        description="날짜 (YYYY-MM-DD HH). 미입력 시 현재 시각 기준.",
        pattern=r"^\d{4}-\d{2}-\d{2} \d{2}$"
    ),
):
    if target_dt_str is None:
        target_dt_str = datetime.now().strftime("%Y-%m-%d %H")
    target_dt = datetime.strptime(target_dt_str, "%Y-%m-%d %H")

    weathers = await weather_service.get_weather_current(lat, lon, target_dt, is_mountain)
    return CurrentWeatherResponse(weathers=weathers)
