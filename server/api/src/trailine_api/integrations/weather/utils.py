from datetime import datetime, timedelta
from typing import Tuple


def get_latest_kma_announcement_dt(target_dt: datetime) -> datetime:
    """
    KMA 발표 시각(02, 05, 08, 11, 14, 17, 20, 23) 중 target_dt와 가장 가까운 과거의 시각을 반환합니다.
    """
    announcement_hours = [2, 5, 8, 11, 14, 17, 20, 23]

    # 현재 시간의 시(hour) 정보를 가져옴
    current_hour = target_dt.hour

    # 발표 시간들 중 current_hour보다 작거나 같은 가장 큰 값을 찾음
    latest_hour = -1
    for hour in reversed(announcement_hours):
        if current_hour >= hour:
            latest_hour = hour
            break

    # 만약 current_hour가 02시 이전이면 전날 23시로 설정
    if latest_hour == -1:
        announcement_dt = target_dt - timedelta(days=1)
        announcement_dt = announcement_dt.replace(hour=23, minute=0, second=0, microsecond=0)
    else:
        announcement_dt = target_dt.replace(hour=latest_hour, minute=0, second=0, microsecond=0)

    return announcement_dt

def is_within_forecast_window(target_dt: datetime, forecast_dt: datetime) -> bool:
    return target_dt <= forecast_dt <= target_dt + timedelta(hours=3)

def set_offset_hours(target_dt: datetime, forecast_at: datetime) -> int:
    target_dt = target_dt.replace(minute=0, second=0, microsecond=0)
    time_detla = forecast_at - target_dt
    seconds = time_detla.total_seconds()
    delta_hours = int(seconds // 3600)
    return delta_hours

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class KmaLccDfsMap:
    # KMA LCC DFS default parameters (short-term forecast grid)
    re_km: float = 6371.00877  # Earth radius (km)
    grid_km: float = 5.0       # grid spacing (km)
    slat1: float = 30.0        # 1st standard parallel (deg)
    slat2: float = 60.0        # 2nd standard parallel (deg)
    olon: float = 126.0        # origin longitude (deg)
    olat: float = 38.0         # origin latitude (deg)
    xo: float = 43.0           # origin x (grid)
    yo: float = 136.0          # origin y (grid)


def latlon_to_kma_grid(lat: float, lon: float, m: KmaLccDfsMap = KmaLccDfsMap()) -> Tuple[int, int]:
    """
    Convert WGS84 lat/lon to KMA short-term forecast grid (x, y) using LCC DFS projection.
    Returns integer grid coordinates (x, y).
    """
    pi = math.pi
    deg2rad = pi / 180.0

    re = m.re_km / m.grid_km
    slat1 = m.slat1 * deg2rad
    slat2 = m.slat2 * deg2rad
    olon = m.olon * deg2rad
    olat = m.olat * deg2rad

    sn = math.tan(pi * 0.25 + slat2 * 0.5) / math.tan(pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)

    sf = math.tan(pi * 0.25 + slat1 * 0.5)
    sf = (sf ** sn) * math.cos(slat1) / sn

    ro = math.tan(pi * 0.25 + olat * 0.5)
    ro = re * sf / (ro ** sn)

    # ---- This block mirrors your C logic ----
    ra = math.tan(pi * 0.25 + (lat * deg2rad) * 0.5)
    ra = re * sf / (ra ** sn)
    theta = (lon * deg2rad) - olon
    if theta > pi:
        theta -= 2.0 * pi
    if theta < -pi:
        theta += 2.0 * pi
    theta *= sn
    x = ra * math.sin(theta) + m.xo
    y = ro - ra * math.cos(theta) + m.yo
    # ----------------------------------------

    # KMA implementations typically round to nearest int with +0.5
    return int(x + 0.5), int(y + 0.5)
