"""Contract tests for the Phase 3 inference endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_infer_returns_stable_orchestration_contract() -> None:
    response = client.post(
        "/api/v1/infer",
        headers={"X-Request-ID": "request-42"},
        json={"prompt": "  Explain   async APIs. ", "task_type": "code", "preferred_backend": "mock-gpt-4o"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["request_id"] == "request-42"
    assert body["status"] == "completed"
    assert body["cached"] is False
    assert body["routing"]["selected_backend"] == "mock-gpt-4o"
    assert "Explain async APIs." in body["output"]
    assert body["quality_score"] == 0.93


def test_infer_rejects_invalid_requests() -> None:
    response = client.post("/api/v1/infer", json={"prompt": "", "max_tokens": 0})

    assert response.status_code == 422
