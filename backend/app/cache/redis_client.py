"""Lazy Redis client lifecycle helpers."""

from functools import lru_cache

from redis.asyncio import Redis, from_url

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> Redis:
    """Return the shared client; network access is deferred until a command runs."""

    return from_url(get_settings().redis_url, decode_responses=True)


async def close_redis() -> None:
    """Close the shared Redis client when the API stops."""

    if get_redis_client.cache_info().currsize:
        await get_redis_client().aclose()
        get_redis_client.cache_clear()
