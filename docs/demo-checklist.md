# NEXUS Demo Checklist

1. Start Ollama and ensure a model is present: `ollama pull gemma3`.
2. Start NEXUS with `docker compose up --build`, or run the API and dashboard
   separately as described in the README.
3. Open the dashboard at `http://localhost:5173` and API docs at
   `http://localhost:8000/docs`.
4. Submit a reasoning prompt with no preferred backend to show Orion routing.
5. Submit the same prompt again to show the semantic-cache hit.
6. Submit a prompt with `preferred_backend: ollama-gemma` to show local model
   integration and a real response.
7. Point out the live event, selected backend, confidence, latency, and cost.

Keep a mock backend as the fallback for a reliable recording if Ollama is busy.
