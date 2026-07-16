# Phase 3: Inference API

## What changed

- `POST /api/v1/infer` accepts a validated, provider-independent request.
- The response includes an inference ID, correlation ID, cache state, output,
  and an explainable routing decision.
- API routes only deserialize HTTP input and delegate to `InferenceService`.

## Why a development executor?

At this stage, a model response must be deterministic, fast, and free. The
development executor makes that explicit instead of hiding a fake vendor
integration. Phase 5 replaces it with adapters; no API consumer needs to
change because the `InferenceResponse` contract already exists.

## Try it

```bash
curl -X POST http://localhost:8000/api/v1/infer ^
  -H "Content-Type: application/json" ^
  -H "X-Request-ID: demo-001" ^
  -d "{\"prompt\": \"Explain async APIs\", \"task_type\": \"code\"}"
```

## Next phase

Create embeddings and a semantic cache implementation that can short-circuit
this service before routing or execution occurs.
