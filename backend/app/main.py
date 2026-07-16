"""FastAPI application assembly; business logic belongs outside this module."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logger import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.cache.redis_client import close_redis
from app.database.session import dispose_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage process-scoped infrastructure clients without eager connections."""

    yield
    await close_redis()
    await dispose_database()


def create_app() -> FastAPI:
    """Build and configure the NEXUS gateway application."""

    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(
        title=f"{settings.app_name} Gateway",
        version="0.1.0",
        description="Intelligent AI inference orchestration gateway.",
        lifespan=lifespan,
    )
    app.add_middleware(RequestContextMiddleware)
    app.include_router(api_router)

    @app.get("/", tags=["system"], summary="Gateway identity")
    async def root() -> dict[str, str]:
        return {"service": settings.app_name, "docs": "/docs"}

    return app


app = create_app()
