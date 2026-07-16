"""Async SQLAlchemy engine and session lifecycle helpers."""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create the shared async session factory without opening a connection yet."""

    engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Yield one transactional-capable session for a request or service action."""

    async with get_session_factory()() as session:
        yield session


async def dispose_database() -> None:
    """Dispose the shared database engine during application shutdown."""

    if get_session_factory.cache_info().currsize:
        await get_session_factory().bind.dispose()  # type: ignore[union-attr]
        get_session_factory.cache_clear()
