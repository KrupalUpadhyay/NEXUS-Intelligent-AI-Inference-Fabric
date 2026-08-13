"""Train Orion from benchmark observations and serialize a deployable policy."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.policy_engine.orion import extract_features  # noqa: E402
from app.schemas.inference import InferenceRequest  # noqa: E402


def score_candidates(candidates: list[dict[str, object]]) -> dict[str, object]:
    """Pick the best available backend using quality, latency, and cost tradeoffs."""

    available = [row for row in candidates if row["available"]]
    if not available:
        available = candidates
    max_latency = max(float(row["latency_ms"] or 1) for row in available)
    max_cost = max(float(row["cost_usd"] or 0.000001) for row in available)
    priority = int(available[0]["user_priority"])
    quality_weight = 0.30 + priority * 0.06
    latency_weight = 0.45 - priority * 0.04
    cost_weight = 1 - quality_weight - latency_weight
    return max(available, key=lambda row: quality_weight * float(row["quality_score"]) - latency_weight * (float(row["latency_ms"] or max_latency) / max_latency) - cost_weight * (float(row["cost_usd"] or max_cost) / max_cost))


def load_examples(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    """Reduce one-row-per-backend observations into supervised routing examples."""

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        grouped[row["workload_id"]].append(row)
    features, labels = [], []
    for candidates in grouped.values():
        winner = score_candidates(candidates)
        request = InferenceRequest.model_validate(candidates[0])
        features.append(extract_features(request))
        labels.append(str(winner["backend"]))
    return features, labels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("training/datasets/benchmark_results.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("backend/models/orion_policy.joblib"))
    args = parser.parse_args()
    features, labels = load_examples(args.input)
    classes = sorted(set(labels))
    class_to_index = {label: index for index, label in enumerate(classes)}
    target = [class_to_index[label] for label in labels]
    pipeline = Pipeline([("vectorizer", DictVectorizer(sparse=False)), ("classifier", RandomForestClassifier(n_estimators=240, max_depth=14, min_samples_leaf=2, class_weight="balanced", n_jobs=-1, random_state=42))])
    train_features, test_features, train_target, test_target = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )
    pipeline.fit(train_features, train_target)
    validation_accuracy = accuracy_score(test_target, pipeline.predict(test_features))
    pipeline.fit(features, target)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "classes": classes, "training_examples": len(features), "validation_accuracy": validation_accuracy}, args.output)
    print(f"Trained Orion on {len(features)} requests; validation_accuracy={validation_accuracy:.3f}; classes={classes}; saved {args.output}")


if __name__ == "__main__":
    main()
