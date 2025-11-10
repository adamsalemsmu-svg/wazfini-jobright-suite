from __future__ import annotations

import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client as TwilioClient

from ..core.config import settings
from ..core.security import anonymize

logger = logging.getLogger(__name__)


def notify_email(*, to: str, subject: str, body: str) -> bool:
    if not settings.SENDGRID_API_KEY or not settings.SENDGRID_FROM_EMAIL:
        logger.info(
            "notification_email_skipped",
            extra={"reason": "sendgrid_not_configured", "recipient": anonymize(to)},
        )
        return False

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=to,
        subject=subject,
        plain_text_content=body,
    )

    try:
        client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        client.send(message)
        logger.info(
            "notification_email_sent",
            extra={"recipient": anonymize(to)},
        )
        return True
    except Exception as exc:  # pragma: no cover - network errors
        logger.warning(
            "notification_email_failed",
            extra={"recipient": anonymize(to), "error": str(exc)},
        )
        return False


def notify_sms(*, to: str, body: str) -> bool:
    if (
        not settings.TWILIO_ACCOUNT_SID
        or not settings.TWILIO_AUTH_TOKEN
        or not settings.TWILIO_FROM_NUMBER
    ):
        logger.info(
            "notification_sms_skipped",
            extra={"reason": "twilio_not_configured", "recipient": anonymize(to)},
        )
        return False

    try:
        client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=settings.TWILIO_FROM_NUMBER,
            to=to,
            body=body,
        )
        logger.info(
            "notification_sms_sent",
            extra={"recipient": anonymize(to)},
        )
        return True
    except Exception as exc:  # pragma: no cover - network errors
        logger.warning(
            "notification_sms_failed",
            extra={"recipient": anonymize(to), "error": str(exc)},
        )
        return False


__all__ = ["notify_email", "notify_sms"]
