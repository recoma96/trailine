import os


class Settings:
    RUN_MODE = os.getenv("RUN_MODE", "dev")

    KMA_API_URL = "https://apihub.kma.go.kr/api"
    KMA_MOUNTAIN_WEATHER_URL = "/typ08/getMountainWeather"
    KMA_API_AUTH_KEY = os.getenv("KMA_API_AUTH_KEY")

    DATAGO_API_URL = "https://apis.data.go.kr"
    DATAGO_VILEAGE_WEATHER_URL = "/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    DATAGO_SERVICE_KEY = os.getenv("DATAGO_SERVICE_KEY")

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_HEALTH_CHECK_INTERVAL = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30"))
