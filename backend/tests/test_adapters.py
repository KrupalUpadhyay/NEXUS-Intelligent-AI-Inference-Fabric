"""Unit tests for adapter behavior and fallback execution."""

import pytest

from app.inference.adapters import MockAdapter, MockProfile
from app.inference.registry import AdapterRegistry
from app.schemas.inference import InferenceRequest


@pytest.mark.anyio
async def test_mock_adapter_reports_simulated_execution_metadata() -> None:
    adapter = MockAdapter("mock", "test", MockProfile(10, 0, 0.01, 0.9, 1.0), simulate_latency=False)

    result = await adapter.infer(InferenceRequest(prompt="test", max_tokens=100))

    assert result.latency_ms == 10
    assert result.estimated_cost_usd > 0
    assert result.quality_score == 0.9


@pytest.mark.anyio
async def test_registry_falls_back_after_unavailable_backend() -> None:
    unavailable = MockAdapter("unavailable", "test", MockProfile(1, 0, 0, 0.5, 0.0), simulate_latency=False)
    healthy = MockAdapter("healthy", "test", MockProfile(1, 0, 0, 0.9, 1.0), simulate_latency=False)
    registry = AdapterRegistry([unavailable, healthy], "unavailable")

    execution = await registry.execute(InferenceRequest(prompt="test"))

    assert execution.backend == "healthy"
    assert len(execution.failures) == 1
