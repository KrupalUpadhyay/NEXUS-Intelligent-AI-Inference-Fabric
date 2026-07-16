"""Embedding providers used by the semantic cache."""

from hashlib import sha256
from math import sqrt
from typing import Protocol


class EmbeddingProvider(Protocol):
    """Produce normalized embedding vectors for semantically comparable text."""

    async def embed(self, text: str) -> list[float]: ...


class HashingEmbeddingProvider:
    """Offline deterministic embedding provider for development and test workflows.

    It is deliberately isolated behind `EmbeddingProvider`; production can swap
    it for a Sentence Transformer without changing cache orchestration.
    """

    def __init__(self, dimensions: int = 256) -> None:
        self._dimensions = dimensions

    async def embed(self, text: str) -> list[float]:
        """Create a normalized token-hash vector without an external model."""

        vector = [0.0] * self._dimensions
        tokens = text.casefold().split()
        for token in tokens:
            digest = sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self._dimensions
            vector[index] += 1 if digest[4] % 2 else -1

        magnitude = sqrt(sum(value * value for value in vector))
        return [value / magnitude for value in vector] if magnitude else vector


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Compute cosine similarity for normalized vectors defensively."""

    if len(left) != len(right):
        raise ValueError("Embedding vectors must use identical dimensions.")
    return sum(a * b for a, b in zip(left, right, strict=True))
