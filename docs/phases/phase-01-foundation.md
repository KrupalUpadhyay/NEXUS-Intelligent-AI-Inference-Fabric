# Phase 1: Foundation

## Objective

Create a small vertical slice that can be started locally and verified before
adding system complexity.

## Decisions

- **FastAPI application factory:** the entry point only composes routes and
  configuration. Future services stay out of controllers.
- **Versioned API router:** all public endpoints live below `/api/v1`, allowing
  compatible evolution later.
- **Typed health contract:** readiness has a stable Pydantic response from day
  one; Docker uses it for dependency health.
- **Static dashboard container:** the React application is built once and served
  by Nginx. Nginx will proxy future API requests under `/api/`.

## Verification

Run `cd backend && pytest`, then `docker compose up --build`. Open the health
endpoint and the dashboard URLs documented in the README.

## Next phase

Add environment-backed configuration, request IDs, structured JSON logs,
middleware, and PostgreSQL/Redis service boundaries.
