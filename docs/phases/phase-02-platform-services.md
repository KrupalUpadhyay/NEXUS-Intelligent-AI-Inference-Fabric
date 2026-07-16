# Phase 2: Platform Services

## What changed

- `Settings` loads validated `NEXUS_` environment variables from the process or
  a local `.env` file.
- Every HTTP response carries an `X-Request-ID`; one structured JSON log records
  its method, path, status, and latency.
- PostgreSQL/pgvector and Redis are Compose services. Their Python clients are
  lazy and are cleaned up at shutdown, so API startup does not hide outages.

## Why this design

Routes remain transport adapters. Future repositories depend on
`get_db_session`, and cache services depend on `get_redis_client`; neither
knows how URLs or containers are configured.

## Verify

```bash
cd backend && pytest
docker compose up --build
```

Inspect a request log and confirm the response `X-Request-ID` matches it.

## Next phase

Define the inference request/response contracts and add the asynchronous
orchestration service behind `POST /api/v1/infer`.
