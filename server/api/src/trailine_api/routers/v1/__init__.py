from fastapi import APIRouter

from trailine_api.routers.v1.health import router as v1_health

router = APIRouter()
router.include_router(v1_health, prefix="/health", tags=["health"])
