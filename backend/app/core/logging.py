from __future__ import annotations

import contextvars
import logging
import sys
import uuid

from pythonjsonlogger import jsonlogger

from .config import settings


_REQUEST_ID_ATTR = "request_id"
_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


class RequestIdFilter(logging.Filter):
    def filter(
        self, record: logging.LogRecord
    ) -> bool:  # pragma: no cover - simple filter
        setattr(record, _REQUEST_ID_ATTR, _request_id.get())
        return True


def configure_logging() -> None:
    formatter = jsonlogger.JsonFormatter(  # type: ignore[attr-defined]
        fmt="%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s",
        rename_fields={"levelname": "level", "name": "logger"},
    )
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    logging.basicConfig(level=settings.LOG_LEVEL, handlers=[handler], force=True)
    logging.getLogger("uvicorn.access").handlers = []


def set_request_id(request_id: str | None) -> None:
    _request_id.set(request_id)


def new_request_id() -> str:
    return uuid.uuid4().hex
