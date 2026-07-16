"""Semantic cache domain service and repository interfaces."""

from dataclasses import dataclass
from typing import Protocol

from app.cache.embeddings import EmbeddingProvider, cosine_similarity
from app.schemas.inference import RoutingDecision, TaskType


@dataclass(frozen=True)
class CachedInference:
    """Data retained after a successful inference for future reuse."""

    task_type: TaskType
    embedding: list[float]
    output: str
    routing: RoutingDecision


@dataclass(frozen=True)
class CacheMatch:
    """A cached value and the similarity score that selected it."""

    entry: CachedInference
    similarity: float


class SemanticCacheRepository(Protocol):
    """Persistence contract for vector similarity cache entries."""

    async def find_nearest(
        self, task_type: TaskType, embedding: list[float], threshold: float
    ) -> CacheMatch | None: ...

    async def save(self, entry: CachedInference) -> None: ...


class InMemorySemanticCacheRepository:
    """Process-local repository for development; PostgreSQL replaces it in deployment."""

    def __init__(self) -> None:
        self._entries: list[CachedInference] = []

    async def find_nearest(
        self, task_type: TaskType, embedding: list[float], threshold: float
    ) -> CacheMatch | None:
        matches = [
            CacheMatch(entry=entry, similarity=cosine_similarity(embedding, entry.embedding))
            for entry in self._entries
            if entry.task_type == task_type
        ]
        best_match = max(matches, key=lambda match: match.similarity, default=None)
        return best_match if best_match and best_match.similarity >= threshold else None

    async def save(self, entry: CachedInference) -> None:
        self._entries.append(entry)


class SemanticCache:
    """Coordinates embeddings and repository similarity lookups."""

    def __init__(
        self, embedding_provider: EmbeddingProvider, repository: SemanticCacheRepository, threshold: float
    ) -> None:
        self._embedding_provider = embedding_provider
        self._repository = repository
        self._threshold = threshold

    async def lookup(self, prompt: str, task_type: TaskType) -> CacheMatch | None:
        """Embed a prompt and return a qualifying nearest cached result."""

        embedding = await self._embedding_provider.embed(prompt)
        return await self._repository.find_nearest(task_type, embedding, self._threshold)

    async def store(self, prompt: str, task_type: TaskType, output: str, routing: RoutingDecision) -> None:
        """Embed and persist a successful response for a later semantic match."""

        embedding = await self._embedding_provider.embed(prompt)
        await self._repository.save(
            CachedInference(task_type=task_type, embedding=embedding, output=output, routing=routing)
        )
