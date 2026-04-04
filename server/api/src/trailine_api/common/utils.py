import math
from typing import Tuple


def latlon_to_grid(lat: float, lon: float) -> Tuple[int, int]:
    """
    기상청 단기예보 위경도(lat, lon)를 격자(nx, ny)로 변환한다.

    Args:
        lat: 위도 (degree)
        lon: 경도 (degree)

    Returns:
        (nx, ny): 정수 격자 좌표
    """
    # 원본 C 코드의 지도 파라미터
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0       # 격자 간격(km)
    SLAT1 = 30.0     # 표준위도 1(degree)
    SLAT2 = 60.0     # 표준위도 2(degree)
    OLON = 126.0     # 기준점 경도(degree)
    OLAT = 38.0      # 기준점 위도(degree)
    XO = 210.0 / GRID
    YO = 675.0 / GRID

    DEGRAD = math.pi / 180.0

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)

    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (sf ** sn) * math.cos(slat1) / sn

    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / (ro ** sn)

    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / (ra ** sn)

    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi

    theta *= sn

    x = ra * math.sin(theta) + XO
    y = ro - ra * math.cos(theta) + YO

    # 원본 C 코드와 동일한 반올림 처리
    nx = int(x + 1.5)
    ny = int(y + 1.5)

    return nx, ny