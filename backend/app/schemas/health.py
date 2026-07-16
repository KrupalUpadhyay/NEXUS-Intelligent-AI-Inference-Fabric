"""Health endpoint response contract."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Public readiness state of the gateway."""

    status: str
    service: str
    version: str
