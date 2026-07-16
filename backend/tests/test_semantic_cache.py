"""Unit tests for semantic-cache behavior without external services."""

import pytest

from app.cache.embeddings import HashingEmbeddingProvider
from app.cache.semantic_cache import InMemorySemanticCacheRepository, SemanticCache
from app.schemas.inference import InferenceRequest, RoutingDecision, TaskType
from app.services.inference_service import DevelopmentInferenceExecutor, InferenceService


@pytest.mark.anyio
async def test_identical_prompt_is_served_from_semantic_cache() -> None:
    cache = SemanticCache(HashingEmbeddingProvider(), InMemorySemanticCacheRepository(), threshold=0.92)
    service = InferenceService(DevelopmentInferenceExecutor(), cache)
    request = InferenceRequest(prompt="Explain vector search", task_type=TaskType.REASONING)

    first = await service.infer(request, "first")
    second = await service.infer(request, "second")

    assert first.cached is False
    assert second.cached is True
    assert second.request_id == "second"
    assert "Semantic cache match" in second.routing.reason[0]


@pytest.mark.anyio
async def test_cache_does_not_cross_task_types() -> None:
    cache = SemanticCache(HashingEmbeddingProvider(), InMemorySemanticCacheRepository(), threshold=0.92)
    routing = RoutingDecision(selected_backend="test", confidence=1, reason=["test"], alternatives=[])
    await cache.store("Translate this sentence", TaskType.TRANSLATION, "result", routing)

    assert await cache.lookup("Translate this sentence", TaskType.CODE) is None
