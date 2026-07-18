"""Top-level API router assembly."""

from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.inference import router as inference_router
from app.api.routes.models import router as models_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["system"])
api_router.include_router(inference_router, tags=["inference"])
api_router.include_router(models_router, tags=["models"])
