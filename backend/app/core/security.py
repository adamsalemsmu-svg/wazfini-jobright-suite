from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InvalidTokenError(Exception):
    """Raised when a JWT is invalid or expired."""


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _pwd_context.verify(password, hashed)
    except Exception:
        return False


def validate_password_strength(password: str) -> None:
    """Raise ValueError if password does not meet policy."""
    if len(password) >= settings.PASSWORD_PASSPHRASE_LENGTH:
        return
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise ValueError("Password does not meet minimum length requirement.")
    score = sum(
        (
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        )
    )
    if score < 3:
        raise ValueError("Password must include a mix of character types.")


def _common_claims(subject: str, token_type: str) -> Dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    return {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "jti": uuid4().hex,
    }


def create_access_token(subject: str) -> Dict[str, Any]:
    payload = _common_claims(subject, "access")
    expire_at = datetime.now(tz=timezone.utc) + settings.access_token_ttl
    payload["exp"] = int(expire_at.timestamp())
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"token": token, "claims": payload}


def create_refresh_token(subject: str) -> Dict[str, Any]:
    payload = _common_claims(subject, "refresh")
    expire_at = datetime.now(tz=timezone.utc) + settings.refresh_token_ttl
    payload["exp"] = int(expire_at.timestamp())
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"token": token, "claims": payload}


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc


def anonymize(value: str | None) -> str | None:
    if value is None:
        return None
    return hashlib.sha256(value.lower().encode("utf-8")).hexdigest()
