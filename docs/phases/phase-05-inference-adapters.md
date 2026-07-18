# Phase 5: Inference Adapters

`ollama-gemma` calls your local Ollama API at `NEXUS_OLLAMA_BASE_URL` using
`NEXUS_OLLAMA_MODEL`. Mock GPT-4o, Claude 4, Llama 3, and Mistral backends
simulate latency, cost, quality, availability, and failure without API keys.

Set `preferred_backend` to select a backend. The default is Ollama/Gemma. If it
is unavailable, NEXUS records the error and falls back to a mock backend.

```powershell
ollama pull gemma3
curl.exe -X POST http://localhost:8000/api/v1/infer -H "Content-Type: application/json" -d '{"prompt":"Explain semantic caching","preferred_backend":"ollama-gemma"}'
```

Use `GET /api/v1/models` to inspect configured backends.
