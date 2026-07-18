"""Tests for the public configured-model catalog."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_models_lists_ollama_and_mock_backends() -> None:
    response = client.get("/api/v1/models")

    assert response.status_code == 200
    assert {model["name"] for model in response.json()} >= {"ollama-gemma", "mock-gpt-4o", "mock-claude-4"}
