# Phases 8–10: Dashboard, Animation, and Production Polish

## Dashboard and live events

The React dashboard polls initial metrics and opens `WS /api/v1/live`. Every
completed inference emits an event with routing, latency, cache, and cost data.
The overview renders backend catalog data from `GET /api/v1/models` and lets a
viewer submit a real request without leaving the page.

## Animation

The inference-path visual is intentionally CSS-native: glowing particles move
through Gateway → Cache → Orion → Adapter → Response. This keeps the dashboard
fast and avoids a visualization dependency for the first demo.

## Operational boundaries

`TelemetryService` is process-local and bounded for the demo. It deliberately
has a narrow interface so Phase 10 deployment work can replace it with Redis
pub/sub and persistent analytics without changing route contracts.

## Final verification

```powershell
cd backend; python -m pytest
cd ../frontend; npm run build
docker compose config
```

Docker Desktop must be running to build/start containers.
