"""Tests for feature extraction and safe untrained-policy behavior."""

from app.policy_engine.orion import OrionPolicyEngine, extract_features
from app.schemas.inference import InferenceRequest, TaskType


def test_orion_extracts_only_pre_inference_features() -> None:
    features = extract_features(InferenceRequest(prompt="Explain caching", task_type=TaskType.REASONING, max_tokens=256, user_priority=8, metadata={"queue_length": "4"}))

    assert features == {"task_type": "reasoning", "prompt_length": 15, "estimated_tokens": 258, "max_tokens": 256, "user_priority": 8, "queue_length": 4}


def test_untrained_orion_returns_no_decision(tmp_path) -> None:
    assert OrionPolicyEngine(str(tmp_path / "missing.joblib")).decide(InferenceRequest(prompt="test")) is None


def test_trained_orion_selects_a_configured_mock_backend() -> None:
    decision = OrionPolicyEngine("models/orion_policy.joblib").decide(
        InferenceRequest(prompt="Write Python code for a rate limiter", task_type=TaskType.CODE, max_tokens=512)
    )

    assert decision is not None
    assert decision.backend in {"mock-gpt-4o", "mock-claude-4", "mock-llama-3", "mock-mistral"}
    assert 0 <= decision.confidence <= 1


def test_orion_can_change_route_without_changing_task_type() -> None:
    engine = OrionPolicyEngine("models/orion_policy.joblib")
    prompt = "Summarize the following distributed systems incident report with risks and action items. " * 30
    low_priority = engine.decide(InferenceRequest(prompt=prompt, task_type=TaskType.SUMMARIZATION, max_tokens=128, user_priority=0, metadata={"queue_length": "0"}))
    high_priority = engine.decide(InferenceRequest(prompt=prompt, task_type=TaskType.SUMMARIZATION, max_tokens=2048, user_priority=10, metadata={"queue_length": "70"}))

    assert low_priority is not None and high_priority is not None
    assert low_priority.backend != high_priority.backend
