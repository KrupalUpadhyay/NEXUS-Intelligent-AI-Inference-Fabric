"""Tests for dashboard-visible telemetry."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_endpoint_returns_dashboard_contract() -> None:
    response = client.get("/api/v1/metrics")

    assert response.status_code == 200
    assert {"total_requests", "cache_hits", "average_latency_ms", "total_cost_usd", "recent_decisions"} <= response.json().keys()
