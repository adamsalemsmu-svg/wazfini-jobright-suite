# ruff: noqa: E402
from __future__ import annotations

import logging
import sys
from pathlib import Path
import os

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.core.db import Base, SessionLocal, engine
from app.core.security import hash_password, verify_password
from app.models import User

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

DEFAULT_USERS = (
    {
        "email": os.getenv("DEMO_USER_EMAIL", "demo@wazifni.ai"),
        "password": os.getenv("DEMO_USER_PASSWORD", "ChangeMe!2024"),
        "full_name": "Demo Candidate",
        "locale": "en",
        "time_zone": "Asia/Dubai",
    },
    {
        "email": os.getenv("SMOKE_USER_EMAIL", "adam@wazifni.ai"),
        "password": os.getenv("SMOKE_USER_PASSWORD", "TestSmoke!2024"),
        "full_name": "Smoke Test Account",
        "locale": "en",
        "time_zone": "UTC",
    },
)


def upsert_user(session: Session, *, email: str, password: str, **attrs: str) -> None:
    existing = session.query(User).filter(User.email == email).first()
    if existing:
        if verify_password(password, existing.password_hash):
            LOGGER.info(
                "User already present", extra={"user_id": existing.id, "email": email}
            )
            return

        existing.password_hash = hash_password(password)
        session.add(existing)
        session.commit()
        LOGGER.info(
            "User password reset", extra={"user_id": existing.id, "email": email}
        )
        return

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=attrs.get("full_name", ""),
        locale=attrs.get("locale", "en"),
        time_zone=attrs.get("time_zone", "UTC"),
    )
    session.add(user)
    session.commit()
    LOGGER.info("User created", extra={"user_id": user.id, "email": email})


def main() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        for user in DEFAULT_USERS:
            upsert_user(session, **user)
    finally:
        session.close()


if __name__ == "__main__":
    main()
