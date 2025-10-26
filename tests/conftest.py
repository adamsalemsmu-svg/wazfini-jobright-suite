from __future__ import annotations

import asyncio
import sys
import time
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Tuple

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.api.deps import require_db  # noqa: E402
from app.core.cache import get_redis  # noqa: E402
from app.core.db import Base  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402


class InMemoryPipeline:
    def __init__(self, redis: "InMemoryRedis") -> None:
        self._redis = redis
        self._ops: List[Tuple[str, Tuple[Any, ...], Dict[str, Any]]] = []

    async def __aenter__(self) -> "InMemoryPipeline":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._ops.clear()

    def setex(self, key: str, ttl: int, value: Any) -> "InMemoryPipeline":
        self._ops.append(("setex", (key, ttl, value), {}))
        return self

    async def execute(self) -> List[Any]:
        results: List[Any] = []
        for method_name, args, kwargs in self._ops:
            method = getattr(self._redis, method_name)
            results.append(await method(*args, **kwargs))
        self._ops.clear()
        return results


class InMemoryRedis:
    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._zsets: Dict[str, Dict[str, float]] = {}
        self.testing_loop = asyncio.new_event_loop()

    def _purge(self) -> None:
        now = time.time()
        expired = [key for key, expires_at in self._expiry.items() if expires_at <= now]
        for key in expired:
            self._store.pop(key, None)
            self._zsets.pop(key, None)
            self._expiry.pop(key, None)

    async def incr(self, key: str) -> int:
        self._purge()
        value = int(self._store.get(key, 0)) + 1
        self._store[key] = value
        return value

    async def expire(self, key: str, seconds: int) -> bool:
        self._purge()
        if key not in self._store and key not in self._zsets:
            return False
        if seconds <= 0:
            self._store.pop(key, None)
            self._zsets.pop(key, None)
            self._expiry.pop(key, None)
            return True
        self._expiry[key] = time.time() + seconds
        return True

    async def setex(self, key: str, seconds: int, value: Any) -> bool:
        self._store[key] = value
        await self.expire(key, seconds)
        return True

    async def getdel(self, key: str) -> Any:
        self._purge()
        value = self._store.pop(key, None)
        self._zsets.pop(key, None)
        self._expiry.pop(key, None)
        return value

    async def delete(self, *keys: str) -> int:
        self._purge()
        removed = 0
        for key in keys:
            if key in self._store or key in self._zsets:
                removed += 1
            self._store.pop(key, None)
            self._zsets.pop(key, None)
            self._expiry.pop(key, None)
        return removed

    async def exists(self, key: str) -> int:
        self._purge()
        return int(key in self._store or key in self._zsets)

    async def ping(self) -> bool:
        return True

    async def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        self._purge()
        zset = self._zsets.setdefault(key, {})
        added = 0
        for member, score in mapping.items():
            if member not in zset:
                added += 1
            zset[member] = float(score)
        return added

    async def zscore(self, key: str, member: str) -> float | None:
        self._purge()
        return self._zsets.get(key, {}).get(member)

    async def zrem(self, key: str, member: str) -> int:
        self._purge()
        zset = self._zsets.get(key)
        if not zset or member not in zset:
            return 0
        del zset[member]
        if not zset:
            self._zsets.pop(key, None)
        return 1

    async def zrange(self, key: str, start: int, end: int, *, withscores: bool = False) -> Iterable[Any]:
        self._purge()
        zset = self._zsets.get(key)
        if not zset:
            return []
        items = sorted(zset.items(), key=lambda item: item[1])
        if end != -1:
            slice_items = items[start : end + 1]
        else:
            slice_items = items[start:]
        if withscores:
            return slice_items
        return [member for member, _ in slice_items]

    async def set(self, key: str, value: Any) -> bool:
        self._store[key] = value
        self._expiry.pop(key, None)
        return True

    async def get(self, key: str) -> Any:
        self._purge()
        return self._store.get(key)

    async def keys(self, pattern: str) -> List[str]:
        self._purge()
        keys = list(self._store.keys()) + list(self._zsets.keys())
        return sorted(key for key in keys if fnmatch(key, pattern))

    def pipeline(self, transaction: bool = False) -> InMemoryPipeline:
        return InMemoryPipeline(self)

    async def close(self) -> None:
        if not self.testing_loop.is_closed():
            self.testing_loop.close()

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def redis_client() -> Generator[InMemoryRedis, None, None]:
    client = InMemoryRedis()
    try:
        yield client
    finally:
        client.testing_loop.close()


@pytest.fixture()
def client(db_session: Session, redis_client: InMemoryRedis) -> Generator[TestClient, None, None]:
    def override_db() -> Generator[Session, None, None]:
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    async def override_redis():
        yield redis_client

    app.dependency_overrides[require_db] = override_db
    app.dependency_overrides[get_redis] = override_redis

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(require_db, None)
    app.dependency_overrides.pop(get_redis, None)


@pytest.fixture()
def create_user(db_session: Session):
    def _create(email: str = "test@example.com", password: str = "StrongPass!123") -> User:
        user = User(email=email, password_hash=hash_password(password))
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create
