from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Tuple

from redis.asyncio import Redis

from ..core.config import settings

_ACTIVE_KEY = "refresh:active:{user_id}"
_REVOKED_KEY = "refresh:revoked:{jti}"


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


async def store_refresh_token(redis: Redis, *, user_id: int, jti: str, expires_at: datetime) -> None:
    key = _ACTIVE_KEY.format(user_id=user_id)
    await redis.zadd(key, {jti: expires_at.timestamp()})
    await redis.expire(key, int(settings.refresh_token_ttl.total_seconds()))


async def refresh_token_is_active(redis: Redis, *, user_id: int, jti: str) -> bool:
    key = _ACTIVE_KEY.format(user_id=user_id)
    score = await redis.zscore(key, jti)
    if score is None:
        return False
    if score < _now().timestamp():
        await redis.zrem(key, jti)
        return False
    return True


async def mark_refresh_token_revoked(redis: Redis, *, user_id: int, jti: str, expires_at: datetime) -> None:
    key = _ACTIVE_KEY.format(user_id=user_id)
    await redis.zrem(key, jti)
    ttl = max(int(expires_at.timestamp() - _now().timestamp()), 1)
    await redis.setex(_REVOKED_KEY.format(jti=jti), ttl, 1)


async def is_refresh_token_revoked(redis: Redis, *, jti: str) -> bool:
    return bool(await redis.exists(_REVOKED_KEY.format(jti=jti)))


async def revoke_all_refresh_tokens(redis: Redis, *, user_id: int) -> None:
    key = _ACTIVE_KEY.format(user_id=user_id)
    items: Iterable[Tuple[str, float]] = await redis.zrange(key, 0, -1, withscores=True)
    await redis.delete(key)
    now_ts = _now().timestamp()
    if not items:
        return
    async with redis.pipeline(transaction=False) as pipe:
        for jti, score in items:
            ttl = max(int(score - now_ts), 1)
            pipe.setex(_REVOKED_KEY.format(jti=jti), ttl, 1)
        await pipe.execute()
