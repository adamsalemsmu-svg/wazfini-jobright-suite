# ruff: noqa: E402
from __future__ import annotations

import logging
import sys
from pathlib import Path

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.core.db import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import User

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

DEMO_EMAIL = "demo@wazifni.ai"
DEMO_PASSWORD = "ChangeMe!2024"


def seed_demo_user(session: Session) -> None:
    existing = session.query(User).filter(User.email == DEMO_EMAIL).first()
    if existing:
        LOGGER.info("Demo user already present", extra={"user_id": existing.id})
        return

    user = User(
        email=DEMO_EMAIL,
        password_hash=hash_password(DEMO_PASSWORD),
        full_name="Demo Candidate",
        locale="en",
        time_zone="Asia/Dubai",
    )
    session.add(user)
    session.commit()
    LOGGER.info("Demo user created", extra={"user_id": user.id})


def main() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed_demo_user(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
