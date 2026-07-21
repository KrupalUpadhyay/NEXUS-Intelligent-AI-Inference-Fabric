# NEXUS — Intelligent AI Inference Fabric

NEXUS is an AI inference orchestration platform that will learn to route each
request to the best available model for latency, cost, and quality. It is being
built in deliberate, independently runnable phases.

## Current status — Complete (Phases 1–10)

This foundation provides a FastAPI gateway, a React dashboard shell, Docker
development environment, health checks, structured request logs, semantic
caching, local Ollama inference, provider simulations, benchmark tooling, and
the learned Orion routing policy, a live dashboard, and production-oriented
testing/documentation polish.

## Architecture (today)

```text
React dashboard  ──HTTP──>  FastAPI gateway
                                  │
                                  └── /api/v1/health
```

## Run locally

Prerequisites: Docker Desktop (recommended), or Python 3.11+ and Node 20+.

```bash
docker compose up --build
```

- Dashboard: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

For non-Docker development:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

## Phase roadmap

1. Repository, Docker, FastAPI, React, health API ✅
2. Configuration, structured logging, middleware, database ✅
3. Inference API and contracts ✅
4. Semantic cache and embeddings ✅
5. Adapter-based inference backends ✅
6. Synthetic workload and benchmarks ✅
7. Orion learned routing policy ✅
8. Observability dashboard ✅
9. Request-flow animations ✅
10. Deployment polish, testing, documentation ✅

## Repository layout

```text
backend/     FastAPI application and tests
frontend/    React/TypeScript dashboard
docker/      Container definitions
docs/        Architecture and phase notes
```

## Useful commands

```bash
# Backend tests
cd backend && pytest

# Frontend type-check and production build
cd frontend && npm run build
```

## Demo

See [the demo checklist](docs/demo-checklist.md) for a reliable recording flow.
