from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from ..models import AuditEvent

_logger = logging.getLogger("audit")


def record_audit_event(
    db: Session,
    *,
    event_type: str,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
) -> AuditEvent:
    payload = details or {}
    event = AuditEvent(user_id=user_id, event_type=event_type, details=payload)
    db.add(event)
    db.commit()
    db.refresh(event)
    _logger.info(
        "audit_event",
        extra={"event_type": event_type, "user_id": user_id, "details": payload},
    )
    return event
