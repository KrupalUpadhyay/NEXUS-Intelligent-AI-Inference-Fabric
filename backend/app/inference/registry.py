"""Backend registry and fallback execution policy."""

from dataclasses import dataclass

from app.inference.adapters import AdapterResult, BackendUnavailableError, BaseAdapter
from app.schemas.inference import InferenceRequest, ModelInfo


@dataclass(frozen=True)
class ExecutionResult:
    """An adapter result paired with its fallback history."""

    backend: str
    result: AdapterResult
    failures: list[str]


class AdapterRegistry:
    """Resolve named adapters and execute ordered fallback candidates."""

    def __init__(self, adapters: list[BaseAdapter], default_backend: str) -> None:
        self._adapters = {adapter.name: adapter for adapter in adapters}
        self._default_backend = default_backend
        if default_backend not in self._adapters:
            raise ValueError(f"Unknown default backend: {default_backend}")

    def list_models(self) -> list[ModelInfo]:
        """Return the public model catalog without exposing provider internals."""

        return [ModelInfo(name=adapter.name, provider=adapter.provider, is_local=adapter.is_local, supported_tasks=list(adapter.supported_tasks)) for adapter in self._adapters.values()]

    def has_backend(self, backend_name: str) -> bool:
        """Return whether this deployment has the named adapter configured."""

        return backend_name in self._adapters

    async def execute(self, request: InferenceRequest) -> ExecutionResult:
        """Try a preferred/default backend, then healthy alternatives in registry order."""

        primary = request.preferred_backend or self._default_backend
        if primary not in self._adapters:
            raise ValueError(f"Unknown backend requested: {primary}")
        candidates = [primary] + [name for name in self._adapters if name != primary]
        failures: list[str] = []
        for backend_name in candidates:
            try:
                result = await self._adapters[backend_name].infer(request)
                return ExecutionResult(backend=backend_name, result=result, failures=failures)
            except BackendUnavailableError as error:
                failures.append(f"{backend_name}: {error}")
        raise BackendUnavailableError("All configured inference backends are unavailable.")
