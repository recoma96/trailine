from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from trailine_api.container import Container
from trailine_api.routers import router as api_router


def create_app() -> FastAPI:
    container = Container()

    app = FastAPI(title="trailine_api")
    app.container = container  # type: ignore[attr-defined]
    app.include_router(api_router, prefix="/api")

    origins = [
        "http://localhost:4321",
        "http://127.0.0.1:4321",
    ]


    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
    )

    return app


app = create_app()
