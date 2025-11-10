# backend/app/core/db.py
from __future__ import annotations

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


def _build_engine_url(raw: str) -> str:
    if raw.startswith("postgresql") and "sslmode=" not in raw:
        sep = "&" if "?" in raw else "?"
        return f"{raw}{sep}sslmode=require"
    return raw


raw_url = settings.DATABASE_URL
connect_args = {"check_same_thread": False} if raw_url.startswith("sqlite") or raw_url.startswith("sqlite+") else {}

engine = create_engine(
    _build_engine_url(raw_url),
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
