"""Model catalog endpoint."""

from fastapi import APIRouter, Depends

from app.schemas.inference import ModelInfo
from app.services.inference_service import InferenceService, get_inference_service

router = APIRouter()


@router.get("/models", response_model=list[ModelInfo], summary="List configured inference backends")
async def list_models(service: InferenceService = Depends(get_inference_service)) -> list[ModelInfo]:
    """Expose model capabilities for API users and the future dashboard."""

    return service.list_models()
