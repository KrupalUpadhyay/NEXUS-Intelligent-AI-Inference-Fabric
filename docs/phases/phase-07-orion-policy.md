# Phase 7: Orion Learned Routing Policy

## Is the dataset large enough?

The earlier 25-request sample was not. NEXUS now trains on 2,000 generated
requests and 8,000 provider observations. This is enough for a stable,
repeatable **demo policy**, not a claim of production-quality routing. Real
deployment needs anonymized production traffic, human quality ratings, and
continuous retraining.

## Train and serve

From the repository root:

```powershell
python training/generate_synthetic_workload.py --count 2000 --seed 42
python training/benchmark_backends.py
python training/train_orion.py
```

The training script labels each request with the backend that maximizes a
priority-sensitive quality/latency/cost objective, trains a Random Forest, and saves
`backend/models/orion_policy.joblib`. The API loads that artifact at startup.
If it is absent, NEXUS safely uses the Phase 5 fallback policy.

## Demo behavior

Leave `preferred_backend` unset: Orion predicts the backend. Set it when you
need to demonstrate a specific adapter, such as local Ollama. The response
contains the selected backend, confidence, and feature-based explanation.
