from fastapi import FastAPI

from trailine_api.container import Container
from trailine_api.routers import router as api_router


def create_app() -> FastAPI:
    container = Container()

    app = FastAPI(title="trailine_api")
    app.container = container  # type: ignore[attr-defined]
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
