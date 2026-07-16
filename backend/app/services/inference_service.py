"""Provider-independent inference orchestration for the Phase 3 API."""

from dataclasses import dataclass
from functools import lru_cache
from uuid import uuid4

from app.cache.embeddings import HashingEmbeddingProvider
from app.cache.semantic_cache import InMemorySemanticCacheRepository, SemanticCache, SemanticCacheRepository
from app.core.config import get_settings
from app.database.session import get_session_factory
from app.schemas.inference import InferenceRequest, InferenceResponse, RoutingDecision


@dataclass(frozen=True)
class DevelopmentInferenceExecutor:
    """Temporary deterministic executor, replaced by adapter selection in Phase 5."""

    async def execute(self, request: InferenceRequest) -> str:
        """Return an explicit development response without contacting a model."""

        normalized_prompt = " ".join(request.prompt.split())
        return f"Development executor accepted ({request.task_type.value}): {normalized_prompt}"


class InferenceService:
    """Coordinate an inference request while preserving a stable API contract."""

    def __init__(
        self, executor: DevelopmentInferenceExecutor | None = None, semantic_cache: SemanticCache | None = None
    ) -> None:
        self._executor = executor or DevelopmentInferenceExecutor()
        settings = get_settings()
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
            )

        output = await self._executor.execute(request)
        routing = RoutingDecision(
            selected_backend="development-stub", confidence=0.0,
            reason=["Phase 3 uses a deterministic development executor.", "Adapter routing is introduced in Phase 5."], alternatives=[],
        )
        await self._semantic_cache.store(request.prompt, request.task_type, output, routing)
        return InferenceResponse(
            inference_id=str(uuid4()),
            request_id=request_id,
            status="completed",
            output=output,
            cached=False,
            routing=routing,
        )


@lru_cache
def get_inference_service() -> InferenceService:
    """Provide the orchestration service as a FastAPI dependency."""

    return InferenceService()
