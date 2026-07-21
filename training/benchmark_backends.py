"""Replay synthetic requests across mock backends and write routing training data."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.inference.adapters import BackendUnavailableError, create_mock_adapters  # noqa: E402
from app.schemas.inference import InferenceRequest  # noqa: E402


async def benchmark(workload: list[dict[str, object]]) -> list[dict[str, object]]:
    """Execute every workload row against every simulated provider backend."""

    rows: list[dict[str, object]] = []
    task_quality = {
        "mock-gpt-4o": {"code": 0.12, "reasoning": 0.12, "ocr": -0.06},
        "mock-claude-4": {"summarization": 0.12, "chat": 0.10, "code": -0.10, "reasoning": -0.10},
        "mock-llama-3": {"embeddings": 0.22, "translation": 0.05, "reasoning": -0.10},
        "mock-mistral": {"translation": 0.20, "chat": 0.03, "ocr": -0.06},
    }
    base_latency = {"mock-gpt-4o": 500, "mock-claude-4": 560, "mock-llama-3": 420, "mock-mistral": 500}
    for request_data in workload:
        request = InferenceRequest.model_validate(request_data)
        queue_length = int(request.metadata["queue_length"])
        for adapter in create_mock_adapters(simulate_latency=False):
            try:
                result = await adapter.infer(request)
                health = 1.0
                available = True
                quality = max(0.1, min(0.99, result.quality_score + task_quality[adapter.name].get(request.task_type.value, 0) - (0.04 if queue_length > 30 else 0)))
                latency = round(base_latency[adapter.name] * (1 + queue_length / 80) * (1 + len(request.prompt) / 20_000), 2)
                rows.append({**request_data, "backend": adapter.name, "available": available, "backend_health": health, "latency_ms": latency if available else None, "cost_usd": result.estimated_cost_usd if available else None, "quality_score": round(quality, 4) if available else 0.0, "response_length": len(result.output) if available else 0})
            except BackendUnavailableError:
                rows.append({**request_data, "backend": adapter.name, "available": False, "latency_ms": None, "cost_usd": None, "quality_score": 0.0, "response_length": 0})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workload", type=Path, default=Path("training/datasets/synthetic_workload.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("training/datasets/benchmark_results.jsonl"))
    args = parser.parse_args()
    workload = [json.loads(line) for line in args.workload.read_text(encoding="utf-8").splitlines()]
    rows = asyncio.run(benchmark(workload))
    args.output.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    print(f"Wrote {len(rows)} benchmark rows to {args.output}")


if __name__ == "__main__":
    main()
