"""Health and readiness endpoints."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Check gateway health")
async def get_health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return a lightweight readiness response without external dependencies."""

    return HealthResponse(status="ok", service=settings.app_name, version=settings.api_version)
