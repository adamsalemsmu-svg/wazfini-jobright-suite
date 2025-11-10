from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

from celery.utils.log import get_task_logger

from ...celery_app import celery_app
from ...core.config import settings
from ..notifications import notify_email, notify_sms
from .runner import AutomationPlatform, run_automation

logger = get_task_logger(__name__)


@celery_app.task(name="automation.run", bind=True)
def automation_run(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    platform = AutomationPlatform(payload["platform"])
    job_url = str(payload["job_url"])
    profile = payload.get("profile") or {}
    resume = payload.get("resume")
    notify_email_target: Optional[str] = payload.get("notify_email")
    notify_phone_target: Optional[str] = payload.get("notify_phone")

    status = "success"
    try:
        run_automation(
            platform=platform,
            job_url=job_url,
            profile=profile,
            resume=resume,
            headless=settings.APP_ENV != "local",
        )
    except Exception as exc:  # pragma: no cover - we log and surface failure
        status = "failed"
        logger.exception("automation_failed", extra={"job_url": job_url, "platform": platform.value})
        raise
    finally:
        if status == "success":
            logger.info(
                "automation_completed",
                extra={"job_url": job_url, "platform": platform.value, "status": status},
            )
        if notify_email_target:
            notify_email(
                to=notify_email_target,
                subject=f"Wazifni job automation {status}",
                body=f"Automation for {job_url} finished with status: {status}.",
            )
        if notify_phone_target:
            notify_sms(
                to=notify_phone_target,
                body=f"Wazifni automation for {job_url} -> {status}",
            )

    return {"status": status, "job_url": job_url, "platform": platform.value}


__all__ = ["automation_run"]
