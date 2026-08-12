"""Model-backed, explainable routing policy for NEXUS inference requests."""

from dataclasses import dataclass
from pathlib import Path

import joblib

from app.schemas.inference import InferenceRequest


@dataclass(frozen=True)
class OrionDecision:
    """A policy selection with confidence and user-facing rationale."""

    backend: str
    confidence: float
    reasons: list[str]


def extract_features(request: InferenceRequest) -> dict[str, object]:
    """Extract online features using only data available before inference."""

    return {
        "task_type": request.task_type.value,
        "prompt_length": len(request.prompt),
        "estimated_tokens": len(request.prompt.split()) + request.max_tokens,
        "max_tokens": request.max_tokens,
        "user_priority": request.user_priority,
        "queue_length": int(request.metadata.get("queue_length", "0")),
    }


class OrionPolicyEngine:
    """Load a serialized learned-routing pipeline and make deterministic decisions."""

    def __init__(self, model_path: str) -> None:
        self._model_path = Path(model_path)
        if not self._model_path.exists() and not self._model_path.is_absolute():
            repository_candidate = Path("backend") / self._model_path
            if repository_candidate.exists():
                self._model_path = repository_candidate
        artifact = joblib.load(self._model_path) if self._model_path.exists() else None
        self._pipeline = artifact["pipeline"] if artifact else None
        self._classes = artifact["classes"] if artifact else []

    @property
    def is_ready(self) -> bool:
        """Whether a trained policy artifact is available for serving."""

        return self._pipeline is not None

    def decide(self, request: InferenceRequest) -> OrionDecision | None:
        """Predict a backend and return a compact explanation of the input factors."""

        if self._pipeline is None:
            return None
        features = extract_features(request)
        probabilities = self._pipeline.predict_proba([features])[0]
        winner_index = int(probabilities.argmax())
        return OrionDecision(
            backend=str(self._classes[winner_index]), confidence=round(float(probabilities[winner_index]), 4),
            reasons=[
                "Orion selected a backend from the learned benchmark policy.",
                f"Task={features['task_type']}, estimated_tokens={features['estimated_tokens']}, queue_length={features['queue_length']}.",
            ],
        )
