"""Environment-backed configuration for the NEXUS API."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings loaded from `NEXUS_`-prefixed environment variables."""

    model_config = SettingsConfigDict(env_prefix="NEXUS_", env_file=".env", extra="ignore")

    app_name: str = "NEXUS"
    environment: str = "development"
    api_version: str = "v1"
    log_level: str = "INFO"
    database_url: str = Field(
        default="postgresql+asyncpg://nexus:nexus@localhost:5432/nexus",
    )
    redis_url: str = "redis://localhost:6379/0"
    semantic_cache_threshold: float = Field(default=0.92, ge=0, le=1)
    embedding_dimensions: int = Field(default=256, ge=8, le=4_096)
    semantic_cache_backend: Literal["memory", "pgvector"] = "memory"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:latest"
    default_backend: str = "ollama-gemma"
    mock_latency_enabled: bool = True
    orion_enabled: bool = True
    orion_model_path: str = "models/orion_policy.joblib"


@lru_cache
def get_settings() -> Settings:
    """Return the process-scoped settings instance."""

    return Settings()
