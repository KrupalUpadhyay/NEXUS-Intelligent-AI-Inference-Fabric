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
    for request_data in workload:
        request = InferenceRequest.model_validate(request_data)
        for adapter in create_mock_adapters(simulate_latency=False):
            try:
                result = await adapter.infer(request)
                rows.append({**request_data, "backend": adapter.name, "available": True, "latency_ms": result.latency_ms, "cost_usd": result.estimated_cost_usd, "quality_score": result.quality_score, "response_length": len(result.output)})
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
