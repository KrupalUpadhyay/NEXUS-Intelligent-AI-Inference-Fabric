"""PostgreSQL/pgvector repository for production semantic-cache persistence."""

import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.cache.semantic_cache import CacheMatch, CachedInference, SemanticCacheRepository
from app.schemas.inference import RoutingDecision, TaskType


class PgvectorSemanticCacheRepository(SemanticCacheRepository):
    """Use pgvector cosine distance to find semantic-cache candidates."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def find_nearest(
        self, task_type: TaskType, embedding: list[float], threshold: float
    ) -> CacheMatch | None:
        vector = "[" + ",".join(str(value) for value in embedding) + "]"
        query = text(
            "SELECT output, routing, 1 - (embedding <=> CAST(:embedding AS vector)) AS similarity "
            "FROM semantic_cache WHERE task_type = :task_type "
            "AND 1 - (embedding <=> CAST(:embedding AS vector)) >= :threshold "
            "ORDER BY embedding <=> CAST(:embedding AS vector) LIMIT 1"
        )
        async with self._session_factory() as session:
            row = (await session.execute(query, {"embedding": vector, "task_type": task_type.value, "threshold": threshold})).mappings().first()
        if row is None:
            return None
        return CacheMatch(
            entry=CachedInference(
                task_type=task_type, embedding=embedding, output=row["output"],
                routing=RoutingDecision.model_validate(row["routing"]),
            ),
            similarity=float(row["similarity"]),
        )

    async def save(self, entry: CachedInference) -> None:
        vector = "[" + ",".join(str(value) for value in entry.embedding) + "]"
        query = text(
            "INSERT INTO semantic_cache (task_type, embedding, output, routing) "
            "VALUES (:task_type, CAST(:embedding AS vector), :output, CAST(:routing AS jsonb))"
        )
        async with self._session_factory() as session:
            await session.execute(query, {"task_type": entry.task_type.value, "embedding": vector, "output": entry.output, "routing": json.dumps(entry.routing.model_dump())})
            await session.commit()
