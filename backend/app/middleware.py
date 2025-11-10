from __future__ import annotations

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .core import logging as logging_core

_logger = logging.getLogger("requests")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        request_id = request.headers.get("x-request-id") or logging_core.new_request_id()
        logging_core.set_request_id(request_id)
        try:
            response = await call_next(request)
        except Exception:
            logging_core.set_request_id(None)
            raise
        response.headers["x-request-id"] = request_id
        _logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
            },
        )
        logging_core.set_request_id(None)
        return response
