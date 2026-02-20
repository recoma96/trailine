from datetime import datetime, timedelta


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
