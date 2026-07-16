"""Smoke tests for the Phase 1 API surface."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_describes_service() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"service": "NEXUS", "docs": "/docs"}


def test_health_endpoint_is_ready() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "NEXUS", "version": "v1"}


def test_request_id_is_generated_and_returned() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"]


def test_request_id_is_preserved_when_provided() -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "trace-123"})

    assert response.headers["X-Request-ID"] == "trace-123"
