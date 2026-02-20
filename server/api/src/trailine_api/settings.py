import os


class Settings:
    RUN_MODE = os.getenv("RUN_MODE", "dev")
    KMA_API_URL = "https://apihub.kma.go.kr/api"
    KMA_MOUNTAIN_WEATHER_URL = "/typ08/getMountainWeather"
    KMA_API_AUTH_KEY = os.getenv("KMA_API_AUTH_KEY")
