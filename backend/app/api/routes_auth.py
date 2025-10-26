from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Dict
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

import logging

from ..core.cache import get_redis
from ..core.config import settings
from ..core.security import (
    InvalidTokenError,
    anonymize,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    validate_password_strength,
    verify_password,
)
from ..models import User
from ..schemas import (
    LoginRequest,
    LogoutRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshRequest,
    TokenPair,
)
from ..services.audit import record_audit_event
from ..services.email import send_password_reset_email
from ..services.login_guard import LoginGuard
from ..services.token_store import (
    is_refresh_token_revoked,
    mark_refresh_token_revoked,
    refresh_token_is_active,
    revoke_all_refresh_tokens,
    store_refresh_token,
)
from .deps import get_current_user, require_db

router = APIRouter(prefix="/auth", tags=["Auth"])


logger = logging.getLogger(__name__)


def _safe_audit(
    *,
    db: Session,
    event_type: str,
    user_id: int | None = None,
    details: Dict[str, object] | None = None,
) -> None:
    try:
        record_audit_event(
            db,
            event_type=event_type,
            user_id=user_id,
            details=details,
        )
    except Exception:  # pragma: no cover - audit is best-effort
        logger.exception("Failed to record audit event", extra={"event_type": event_type})


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host or "unknown"
    return "unknown"


def _lockout_exception(retry_after_seconds: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Too many attempts. Try again later.",
        headers={"Retry-After": str(retry_after_seconds)},
    )


@router.post(
    "/login",
    response_model=TokenPair,
    responses={
        401: {"description": "Invalid credentials"},
        429: {"description": "Too many attempts"},
    },
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(require_db),
    redis: Redis = Depends(get_redis),
):
    ip_address = _client_ip(request)
    guard = LoginGuard(redis)

    try:
        locked = await guard.is_locked(ip_address, payload.email)
    except Exception:  # pragma: no cover - defensive guard
        logger.exception("Login guard lock check failed; continuing without lockout")
        locked = False

    if locked:
        _safe_audit(
            db=db,
            event_type="auth.login.locked",
            details={"ip": anonymize(ip_address), "email": anonymize(payload.email)},
        )
        raise _lockout_exception(int(guard.retry_after.total_seconds()))

    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        try:
            attempts = await guard.register_failure(ip_address, payload.email)
        except Exception:  # pragma: no cover - defensive guard
            logger.exception("Login guard failure tracking failed")
            attempts = guard.limit
        _safe_audit(
            db=db,
            event_type="auth.login.failure",
            user_id=user.id if user else None,
            details={
                "ip": anonymize(ip_address),
                "email": anonymize(payload.email),
                "attempts": attempts,
            },
        )
        if attempts > guard.limit:
            raise _lockout_exception(int(guard.retry_after.total_seconds()))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    await guard.clear_attempts(ip_address, payload.email)
    _safe_audit(
        db=db,
        event_type="auth.login.success",
        user_id=user.id,
        details={"ip": anonymize(ip_address)},
    )
    try:
        await guard.clear_attempts(ip_address, payload.email)
    except Exception:  # pragma: no cover - defensive guard
        logger.exception("Login guard cleanup failed")
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    refresh_exp = datetime.fromtimestamp(refresh["claims"]["exp"], tz=timezone.utc)

    await store_refresh_token(
        redis,
        user_id=user.id,
        jti=refresh["claims"]["jti"],
        expires_at=refresh_exp,
    )

    return TokenPair(access_token=access["token"], refresh_token=refresh["token"])


@router.post("/refresh", response_model=TokenPair)
async def refresh(
    payload: RefreshRequest,
    db: Session = Depends(require_db),
    redis: Redis = Depends(get_redis),
):
    try:
        decoded = decode_token(payload.refresh_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    token_type = decoded.get("type")
    subject = decoded.get("sub")
    if token_type != "refresh" or subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_id = int(subject)
    jti = decoded["jti"]

    if await is_refresh_token_revoked(redis, jti=jti):
        await revoke_all_refresh_tokens(redis, user_id=user_id)
        record_audit_event(
            db,
            event_type="auth.refresh.reuse_detected",
            user_id=user_id,
            details={"jti": jti},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token reuse detected"
        )

    if not await refresh_token_is_active(redis, user_id=user_id, jti=jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    expires_at = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    await mark_refresh_token_revoked(
        redis, user_id=user_id, jti=jti, expires_at=expires_at
    )

    new_access = create_access_token(str(user_id))
    new_refresh = create_refresh_token(str(user_id))
    new_refresh_exp = datetime.fromtimestamp(
        new_refresh["claims"]["exp"], tz=timezone.utc
    )

    await store_refresh_token(
        redis,
        user_id=user_id,
        jti=new_refresh["claims"]["jti"],
        expires_at=new_refresh_exp,
    )

    record_audit_event(db, event_type="auth.refresh.success", user_id=user_id)
    return TokenPair(
        access_token=new_access["token"], refresh_token=new_refresh["token"]
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(require_db),
    redis: Redis = Depends(get_redis),
):
    if payload.logout_all:
        await revoke_all_refresh_tokens(redis, user_id=current_user.id)
        record_audit_event(db, event_type="auth.logout.all", user_id=current_user.id)
        return

    if not payload.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token required"
        )

    try:
        decoded = decode_token(payload.refresh_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
        )

    token_type = decoded.get("type")
    subject = decoded.get("sub")
    if token_type != "refresh" or subject is None or int(subject) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
        )

    expires_at = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    await mark_refresh_token_revoked(
        redis,
        user_id=current_user.id,
        jti=decoded["jti"],
        expires_at=expires_at,
    )
    record_audit_event(
        db,
        event_type="auth.logout.single",
        user_id=current_user.id,
        details={"jti": decoded["jti"]},
    )


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def password_reset_request(
    payload: PasswordResetRequest,
    request: Request,
    db: Session = Depends(require_db),
    redis: Redis = Depends(get_redis),
):
    ip_address = _client_ip(request)
    hashed_email = anonymize(payload.email)
    limit = settings.LOGIN_ATTEMPT_LIMIT
    window_seconds = int(settings.password_reset_token_ttl.total_seconds())

    for identifier in (hashed_email, ip_address):
        key = f"pwdreset:attempts:{identifier}"
        attempts = await redis.incr(key)
        if attempts == 1:
            await redis.expire(key, window_seconds)
        if attempts > limit:
            raise _lockout_exception(window_seconds)

    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user:
        token_data: Dict[str, str] = {
            "user_id": str(user.id),
            "ip": anonymize(ip_address) or "unknown",
        }
        token = uuid4().hex
        await redis.setex(
            f"pwdreset:{token}",
            window_seconds,
            json.dumps(token_data),
        )
        await send_password_reset_email(recipient=user.email, token=token)
        record_audit_event(
            db,
            event_type="auth.password_reset.request",
            user_id=user.id,
            details={"ip": token_data["ip"]},
        )

    return {"message": "If the email exists, reset instructions have been sent."}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def password_reset_confirm(
    payload: PasswordResetConfirm,
    db: Session = Depends(require_db),
    redis: Redis = Depends(get_redis),
):
    key = f"pwdreset:{payload.token}"
    raw = await redis.getdel(key)
    if raw is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    data: Dict[str, str] = json.loads(raw)
    user_id = int(data["user_id"])

    validate_password_strength(payload.new_password)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    user.password_hash = hash_password(payload.new_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    await revoke_all_refresh_tokens(redis, user_id=user.id)

    record_audit_event(
        db,
        event_type="auth.password_reset.confirm",
        user_id=user.id,
        details={"ip": data.get("ip")},
    )

    return {"message": "Password successfully updated."}
