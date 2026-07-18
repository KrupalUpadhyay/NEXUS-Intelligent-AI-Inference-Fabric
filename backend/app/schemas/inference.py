"""Public contracts for inference orchestration."""

from enum import Enum

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Supported workload categories used by future routing policies."""

    CHAT = "chat"
    SUMMARIZATION = "summarization"
    REASONING = "reasoning"
    TRANSLATION = "translation"
    CODE = "code"
    OCR = "ocr"
    EMBEDDINGS = "embeddings"


class InferenceRequest(BaseModel):
    """Validated, provider-agnostic input accepted by the inference gateway."""

    prompt: str = Field(min_length=1, max_length=32_000, examples=["Summarize this report."])
    task_type: TaskType = TaskType.CHAT
    max_tokens: int = Field(default=512, ge=1, le=8_192)
    user_priority: int = Field(default=5, ge=0, le=10)
    metadata: dict[str, str] = Field(default_factory=dict)
    preferred_backend: str | None = Field(default=None, max_length=64)


class RoutingDecision(BaseModel):
    """Explainable decision data that remains stable across routing iterations."""

    selected_backend: str
    confidence: float = Field(ge=0, le=1)
    reason: list[str]
    alternatives: list[str]


class InferenceResponse(BaseModel):
    """Result returned immediately by the inference orchestration boundary."""

    inference_id: str
    request_id: str
    status: str
    output: str
    cached: bool
    routing: RoutingDecision
    latency_ms: float = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0)
    quality_score: float = Field(ge=0, le=1)


class ModelInfo(BaseModel):
    """Public health and capability summary for an inference backend."""

    name: str
    provider: str
    is_local: bool
    supported_tasks: list[TaskType]
