from fastapi import APIRouter

from trailine_api.routers.v1.health import router as v1_health
from trailine_api.routers.v1.course import router as v1_course
from trailine_api.routers.v1.weather import router as v1_weather


router = APIRouter()
router.include_router(v1_health, prefix="/health", tags=["health"])
router.include_router(v1_course, prefix="/courses", tags=["course"])
router.include_router(v1_weather, prefix="/weather", tags=["weather"])
