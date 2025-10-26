from __future__ import annotations

from datetime import timedelta

from redis.asyncio import Redis

from ..core.config import settings

_ATTEMPT_KEY = "login:attempts:{identifier}"
_LOCK_KEY = "lockout:{identifier}"


class LoginGuard:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.limit = settings.LOGIN_ATTEMPT_LIMIT
        self.lockout_ttl_seconds = int(settings.login_lockout_ttl.total_seconds())

    @staticmethod
    def _attempts_identifier(ip: str, username: str) -> list[str]:
        lowered = username.lower()
        return [ip, lowered]

    async def is_locked(self, ip: str, username: str) -> bool:
        identifiers = self._attempts_identifier(ip, username)
        for ident in identifiers:
            if await self.redis.exists(_LOCK_KEY.format(identifier=ident)):
                return True
        return False

    async def register_failure(self, ip: str, username: str) -> int:
        identifiers = self._attempts_identifier(ip, username)
        max_attempts = 0
        for ident in identifiers:
            key = _ATTEMPT_KEY.format(identifier=ident)
            attempts = await self.redis.incr(key)
            if attempts == 1:
                await self.redis.expire(key, self.lockout_ttl_seconds)
            max_attempts = max(max_attempts, attempts)
            if attempts > self.limit:
                await self.redis.setex(
                    _LOCK_KEY.format(identifier=ident), self.lockout_ttl_seconds, 1
                )
        return max_attempts

    async def clear_attempts(self, ip: str, username: str) -> None:
        identifiers = self._attempts_identifier(ip, username)
        for ident in identifiers:
            await self.redis.delete(_ATTEMPT_KEY.format(identifier=ident))
            await self.redis.delete(_LOCK_KEY.format(identifier=ident))

    @property
    def retry_after(self) -> timedelta:
        return settings.login_lockout_ttl
