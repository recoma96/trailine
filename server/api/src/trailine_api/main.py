from fastapi import FastAPI

from trailine_api.routers import router as api_router

app = FastAPI(title=__name__)


app.include_router(api_router, prefix="/api")
