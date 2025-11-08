from fastapi import APIRouter

from trailine_api.routers.v2.health import router as v2_health

router = APIRouter()
router.include_router(v2_health, prefix="/health", tags=["health"])
