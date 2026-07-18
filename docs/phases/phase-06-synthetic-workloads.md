# Phase 6: Synthetic Workloads and Benchmarks

```powershell
python training/generate_synthetic_workload.py --count 500
python training/benchmark_backends.py
```

The generator writes reproducible task-diverse requests. The benchmark writes
four rows per request (one per mock backend) with latency, cost, quality,
availability, and response-length observations. Phase 7 derives the best
backend label from this data to train Orion.

Ollama is intentionally excluded from repeatable benchmark generation: local
hardware makes its wall-clock latency non-portable. It remains the real local
demonstration backend through the API.
