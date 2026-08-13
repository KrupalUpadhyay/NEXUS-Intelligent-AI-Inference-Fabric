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
        "mock-gpt-4o": {"code": 0.08, "reasoning": 0.08, "ocr": -0.03},
        "mock-claude-4": {"summarization": 0.10, "chat": 0.08, "code": -0.02},
        "mock-llama-3": {"embeddings": 0.14, "translation": 0.03, "reasoning": -0.05},
        "mock-mistral": {"translation": 0.15, "chat": 0.02, "ocr": -0.03},
    }
    base_latency = {"mock-gpt-4o": 560, "mock-claude-4": 650, "mock-llama-3": 290, "mock-mistral": 390}
    queue_penalty = {"mock-gpt-4o": 0.010, "mock-claude-4": 0.008, "mock-llama-3": 0.045, "mock-mistral": 0.025}
    output_penalty = {"mock-gpt-4o": 0.00005, "mock-claude-4": 0.00004, "mock-llama-3": 0.00012, "mock-mistral": 0.00008}
    for request_data in workload:
        request = InferenceRequest.model_validate(request_data)
        queue_length = int(request.metadata["queue_length"])
        prompt_words = len(request.prompt.split())
        complexity = min(1.0, (prompt_words / 130) + (request.max_tokens / 5000))
        for adapter in create_mock_adapters(simulate_latency=False):
            try:
                result = await adapter.infer(request)
                health = 1.0
                available = True
                complexity_bonus = {
                    "mock-gpt-4o": 0.10 * complexity,
                    "mock-claude-4": 0.12 * complexity,
                    "mock-llama-3": 0.08 * (1 - complexity),
                    "mock-mistral": 0.05 * (1 - complexity),
                }[adapter.name]
                quality = max(0.1, min(0.99, result.quality_score + task_quality[adapter.name].get(request.task_type.value, 0) + complexity_bonus))
                latency = round(base_latency[adapter.name] * (1 + queue_length * queue_penalty[adapter.name]) * (1 + request.max_tokens * output_penalty[adapter.name]), 2)
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
