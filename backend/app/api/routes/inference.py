"""Inference API transport layer."""

from fastapi import APIRouter, Depends, Request, status

from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.inference_service import InferenceService, get_inference_service

router = APIRouter()


@router.post(
    "/infer",
    response_model=InferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit an inference request",
)
async def infer(
    payload: InferenceRequest,
    request: Request,
    service: InferenceService = Depends(get_inference_service),
) -> InferenceResponse:
    """Delegate validated work to the inference orchestration service."""

    return await service.infer(payload, request.state.request_id)
