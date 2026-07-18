"""Provider-independent inference orchestration for the Phase 3 API."""

from functools import lru_cache
from uuid import uuid4

from app.cache.embeddings import HashingEmbeddingProvider
from app.cache.semantic_cache import InMemorySemanticCacheRepository, SemanticCache, SemanticCacheRepository
from app.core.config import get_settings
from app.database.session import get_session_factory
from app.inference.adapters import OllamaAdapter, create_mock_adapters
from app.inference.registry import AdapterRegistry
from app.schemas.inference import InferenceRequest, InferenceResponse, ModelInfo, RoutingDecision


class InferenceService:
    """Coordinate an inference request while preserving a stable API contract."""

    def __init__(
        self, registry: AdapterRegistry | None = None, semantic_cache: SemanticCache | None = None
    ) -> None:
        settings = get_settings()
        self._registry = registry or create_adapter_registry()
        repository: SemanticCacheRepository = InMemorySemanticCacheRepository()
        if settings.semantic_cache_backend == "pgvector":
            from app.cache.pgvector_repository import PgvectorSemanticCacheRepository

            repository = PgvectorSemanticCacheRepository(get_session_factory())
        self._semantic_cache = semantic_cache or SemanticCache(
            HashingEmbeddingProvider(settings.embedding_dimensions), repository, settings.semantic_cache_threshold
        )

    async def infer(self, request: InferenceRequest, request_id: str) -> InferenceResponse:
        """Execute the current inference strategy and provide routing explainability."""

        cache_match = await self._semantic_cache.lookup(request.prompt, request.task_type)
        if cache_match:
            return InferenceResponse(
                inference_id=str(uuid4()), request_id=request_id, status="completed", output=cache_match.entry.output,
                cached=True,
                routing=cache_match.entry.routing.model_copy(update={"reason": [f"Semantic cache match ({cache_match.similarity:.2%} similarity)."] + cache_match.entry.routing.reason}),
                latency_ms=0.0,
                estimated_cost_usd=0.0,
                quality_score=cache_match.entry.routing.confidence,
            )

        execution = await self._registry.execute(request)
        routing = RoutingDecision(
            selected_backend=execution.backend,
            confidence=execution.result.quality_score,
            reason=["Selected by Phase 5 fallback policy."] + execution.failures,
            alternatives=[model.name for model in self._registry.list_models() if model.name != execution.backend],
        )
        await self._semantic_cache.store(request.prompt, request.task_type, execution.result.output, routing)
        return InferenceResponse(
            inference_id=str(uuid4()),
            request_id=request_id,
            status="completed",
            output=execution.result.output,
            cached=False,
            routing=routing,
            latency_ms=execution.result.latency_ms,
            estimated_cost_usd=execution.result.estimated_cost_usd,
            quality_score=execution.result.quality_score,
        )

    def list_models(self) -> list[ModelInfo]:
        """Return configured adapter metadata for the API and dashboard."""

        return self._registry.list_models()


def create_adapter_registry() -> AdapterRegistry:
    """Build the Phase 5 adapter catalog from environment-backed settings."""

    settings = get_settings()
    adapters = [OllamaAdapter(settings.ollama_base_url, settings.ollama_model), *create_mock_adapters(settings.mock_latency_enabled)]
    return AdapterRegistry(adapters, settings.default_backend)


@lru_cache
def get_inference_service() -> InferenceService:
    """Provide the orchestration service as a FastAPI dependency."""

    return InferenceService()
