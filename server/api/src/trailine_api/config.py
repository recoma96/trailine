import os


class Config:
    DATAGO_SERVICE_KEY = os.environ.get("DATAGO_SERVICE_KEY")
    REDIS_URL = os.environ.get("REDIS_URL")
    REDIS_HEALTH_CHECK_INTERVAL = os.environ.get("REDIS_HEALTH_CHECK_INTERVAL", 30)
    RUN_MODE = os.environ.get("RUN_MODE", "dev")
