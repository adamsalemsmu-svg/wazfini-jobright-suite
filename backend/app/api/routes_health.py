from __future__ import annotations

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..core.cache import get_redis
from .deps import require_db

router = APIRouter(tags=["Health"])


@router.get("/healthz")
async def healthz() -> dict[str, bool]:
    return {"ok": True}


@router.get("/readyz")
async def readyz(
    db: Session = Depends(require_db),
    redis: Redis = Depends(get_redis),
) -> dict[str, bool]:
    db.execute(text("SELECT 1"))
    await redis.ping()
    return {"ok": True}
