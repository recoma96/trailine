import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from trailine_api.common.logger import setup_logging
from trailine_api.container import Container
from trailine_api.middlewares.request_logger import RequestLoggingMiddleware
from trailine_api.routers import router as api_router


def create_app() -> FastAPI:
    container = Container()

    setup_logging(level="INFO")

    app = FastAPI(
        title="trailine_api",
        docs_url="/api/docs" if os.getenv("APP_ENV") != "prod" else None,
        redoc_url="/api/redoc" if os.getenv("APP_ENV") != "prod" else None,
        openapi_url="/api/openapi.json"  if os.getenv("APP_ENV") != "prod" else None,
    )
    app.container = container  # type: ignore[attr-defined]
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(api_router, prefix="/api")

    if os.getenv("APP_ENV") != "prod":
        origins = [
            # docker local test
            "http://localhost",
            "http://127.0.0.1",

            # for devlopment in local
            "http://localhost:4321",
            "http://127.0.0.1:4321",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ]
    else:
        origins = []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
    )

    return app


app = create_app()
