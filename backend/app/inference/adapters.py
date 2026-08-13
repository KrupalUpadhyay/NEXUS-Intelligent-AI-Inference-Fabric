"""Adapter implementations for local Ollama and realistic provider simulations."""

import asyncio
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from time import perf_counter

import httpx

from app.schemas.inference import InferenceRequest, TaskType


class BackendUnavailableError(RuntimeError):
    """Raised when a backend cannot safely serve the current request."""


@dataclass(frozen=True)
class AdapterResult:
    """Normalized result returned by every model backend."""

    output: str
    latency_ms: float
    estimated_cost_usd: float
    quality_score: float


class BaseAdapter(ABC):
    """Stable integration boundary implemented by every inference backend."""

    name: str
    provider: str
    is_local: bool = False
    supported_tasks: tuple[TaskType, ...] = tuple(TaskType)

    @abstractmethod
    async def infer(self, request: InferenceRequest) -> AdapterResult:
        """Run inference and normalize the provider-specific response."""


class OllamaAdapter(BaseAdapter):
    """Run Gemma or another installed local model through Ollama's HTTP API."""

    name = "ollama-gemma"
    provider = "ollama"
    is_local = True

    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def infer(self, request: InferenceRequest) -> AdapterResult:
        started_at = perf_counter()
        payload = {"model": self._model, "prompt": request.prompt, "stream": False, "options": {"num_predict": request.max_tokens}}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self._base_url}/api/generate", json=payload)
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise BackendUnavailableError(f"Ollama backend unavailable: {error}") from error
        body = response.json()
        output = body.get("response")
        if not isinstance(output, str) or not output.strip():
            raise BackendUnavailableError("Ollama returned an empty response.")
        latency_ms = round((perf_counter() - started_at) * 1_000, 2)
        return AdapterResult(output=output.strip(), latency_ms=latency_ms, estimated_cost_usd=0.0, quality_score=0.72)


@dataclass(frozen=True)
class MockProfile:
    """Behavior profile used to simulate a paid model backend honestly."""

    latency_ms: int
    latency_jitter_ms: int
    cost_per_1k_tokens: float
    quality_score: float
    availability: float


class MockAdapter(BaseAdapter):
    """Simulate latency, availability, cost, and quality without vendor calls."""

    def __init__(self, name: str, provider: str, profile: MockProfile, simulate_latency: bool = True) -> None:
        self.name = name
        self.provider = provider
        self._profile = profile
        self._simulate_latency = simulate_latency

    async def infer(self, request: InferenceRequest) -> AdapterResult:
        if random.random() > self._profile.availability:
            raise BackendUnavailableError(f"{self.name} simulated an availability failure.")
        latency_ms = max(1, self._profile.latency_ms + random.randint(-self._profile.latency_jitter_ms, self._profile.latency_jitter_ms))
        if self._simulate_latency:
            await asyncio.sleep(latency_ms / 1_000)
        estimated_tokens = max(1, len(request.prompt.split()) + request.max_tokens)
        cost = round((estimated_tokens / 1_000) * self._profile.cost_per_1k_tokens, 6)
        normalized_prompt = " ".join(request.prompt.split())
        return AdapterResult(
            output=f"[{self.name} simulated response] {normalized_prompt}", latency_ms=float(latency_ms),
            estimated_cost_usd=cost, quality_score=self._profile.quality_score,
        )


def create_mock_adapters(simulate_latency: bool) -> list[MockAdapter]:
    """Create reproducible paid-provider simulations for development and training."""

    return [
        MockAdapter("mock-gpt-4o", "openai", MockProfile(500, 130, 0.006, 0.88, 0.995), simulate_latency),
        MockAdapter("mock-claude-4", "anthropic", MockProfile(650, 175, 0.008, 0.95, 0.994), simulate_latency),
        MockAdapter("mock-llama-3", "meta", MockProfile(420, 120, 0.002, 0.78, 0.99), simulate_latency),
        MockAdapter("mock-mistral", "mistral", MockProfile(500, 140, 0.003, 0.82, 0.992), simulate_latency),
    ]
