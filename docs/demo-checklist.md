# NEXUS Demo Checklist

1. Start NEXUS with `docker compose up --build`, or run the API and dashboard
   separately as described in the README.
2. Open the dashboard at `http://localhost:5173` and API docs at
   `http://localhost:8000/docs`.
3. Submit a reasoning prompt with no preferred backend to show Orion routing.
4. Submit the same prompt again to show the semantic-cache hit.
5. Submit a prompt with `preferred_backend: mock-gpt-4o` to demonstrate
   deterministic provider simulation and explain that real vendor adapters can
   replace it without API contract changes.
6. Point out the live event, selected backend, confidence, latency, and cost.

Ollama/Gemma is an optional adapter. The full demo works without it.
