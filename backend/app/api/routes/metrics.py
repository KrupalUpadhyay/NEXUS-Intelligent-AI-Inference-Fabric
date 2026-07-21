"""Metrics and live-update endpoints for the NEXUS dashboard."""

from dataclasses import asdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.analytics.telemetry import telemetry

router = APIRouter()


@router.get("/metrics", summary="Get current inference metrics")
async def get_metrics() -> dict[str, object]:
    """Return the dashboard's current aggregate telemetry snapshot."""

    return asdict(telemetry.snapshot())


@router.websocket("/live")
async def live_updates(websocket: WebSocket) -> None:
    """Stream completed inference events to dashboard clients."""

    await websocket.accept()
    queue = telemetry.subscribe()
    try:
        await websocket.send_json({"type": "snapshot", "metrics": asdict(telemetry.snapshot())})
        while True:
            await websocket.send_json(await queue.get())
    except WebSocketDisconnect:
        pass
    finally:
        telemetry.unsubscribe(queue)
