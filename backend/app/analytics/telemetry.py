"""In-process telemetry for dashboard metrics and WebSocket demonstrations."""

import asyncio
from collections import deque
from dataclasses import asdict, dataclass

from app.schemas.inference import InferenceResponse


@dataclass(frozen=True)
class TelemetrySnapshot:
    """Aggregate metrics rendered by the overview dashboard."""

    total_requests: int
    cache_hits: int
    average_latency_ms: float
    total_cost_usd: float
    recent_decisions: list[dict[str, object]]


class TelemetryService:
    """Collect bounded process-local metrics and fan out live inference events."""

    def __init__(self) -> None:
        self._events: deque[dict[str, object]] = deque(maxlen=50)
        self._subscribers: set[asyncio.Queue[dict[str, object]]] = set()
        self._total_requests = 0
        self._cache_hits = 0
        self._latency_total = 0.0
        self._cost_total = 0.0

    async def record_inference(self, response: InferenceResponse) -> None:
        """Record a completed inference and broadcast it to live dashboard clients."""

        event = {"type": "inference_completed", "inference": response.model_dump(mode="json")}
        self._total_requests += 1
        self._cache_hits += int(response.cached)
        self._latency_total += response.latency_ms
        self._cost_total += response.estimated_cost_usd
        self._events.appendleft(event)
        for subscriber in self._subscribers:
            if not subscriber.full():
                subscriber.put_nowait(event)

    def snapshot(self) -> TelemetrySnapshot:
        """Return a serializable point-in-time metrics summary."""

        average = self._latency_total / self._total_requests if self._total_requests else 0.0
        decisions = [event["inference"] for event in self._events]
        return TelemetrySnapshot(self._total_requests, self._cache_hits, round(average, 2), round(self._cost_total, 6), decisions)

    def subscribe(self) -> asyncio.Queue[dict[str, object]]:
        """Register a bounded event queue for one WebSocket client."""

        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=20)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, object]]) -> None:
        """Release a disconnected WebSocket subscriber."""

        self._subscribers.discard(queue)


telemetry = TelemetryService()
