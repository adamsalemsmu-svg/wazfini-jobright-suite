from __future__ import annotations

import asyncio
from typing import AsyncGenerator

from urllib.parse import urlparse

from redis.asyncio import Redis

try:
    import fakeredis.aioredis  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    fakeredis = None  # type: ignore
else:
    fakeredis = fakeredis.aioredis  # type: ignore

from .config import settings

_redis_lock = asyncio.Lock()
_redis_client: Redis | None = None


async def get_redis() -> AsyncGenerator[Redis, None]:
    global _redis_client
    if _redis_client is None:
        async with _redis_lock:
            if _redis_client is None:
                parsed = urlparse(settings.REDIS_URL)
                if parsed.scheme in {"fakeredis", "memory"}:
                    if fakeredis is None:
                        raise RuntimeError(
                            "fakeredis is not installed but REDIS_URL requests it"
                        )
                    _redis_client = fakeredis.FakeRedis(decode_responses=True)
                else:
                    _redis_client = Redis.from_url(
                        settings.REDIS_URL,
                        decode_responses=True,
                        socket_timeout=5,
                        retry_on_timeout=True,
                    )
    try:
        yield _redis_client  # type: ignore[misc]
    finally:
        # Connection is shared; do not close per-request
        pass


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
