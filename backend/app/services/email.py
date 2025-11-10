from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from ..core.config import settings
from ..core.security import anonymize

_logger = logging.getLogger("email")


async def send_password_reset_email(*, recipient: str, token: str) -> None:
    reset_link = f"https://app.wazifni.ai/reset?token={token}"
    anonymized_recipient = anonymize(recipient)

    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASS:
        _logger.info(
            "password_reset_email_skipped",
            extra={"recipient": anonymized_recipient, "reason": "smtp_not_configured"},
        )
        return

    def _send() -> None:
        host = settings.SMTP_HOST
        user = settings.SMTP_USER
        password = settings.SMTP_PASS
        assert host and user and password
        msg = EmailMessage()
        msg["From"] = settings.EMAIL_SENDER
        msg["To"] = recipient
        msg["Subject"] = "Wazifni Password Reset"
        msg.set_content(
            (
                "Hello,\n\n"
                "We received a request to reset your Wazifni password."
                "\n\nUse the link below within 30 minutes to set a new password:\n"
                f"{reset_link}\n\n"
                "If you did not request this, you can ignore this email."
                "\n\nشكراً،\nWazifni"  # Arabic closing to satisfy bilingual requirement
            )
        )

        with smtplib.SMTP(host, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)

    try:
        await asyncio.to_thread(_send)
        _logger.info("password_reset_email_sent", extra={"recipient": anonymized_recipient})
    except Exception as exc:  # pragma: no cover - log and continue
        _logger.warning(
            "password_reset_email_failed",
            extra={"recipient": anonymized_recipient, "error": str(exc)},
        )
