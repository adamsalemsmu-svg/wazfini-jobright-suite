from __future__ import annotations

from enum import Enum
from typing import Mapping, Optional
from . import bayt, greenhouse, workday
from .base import ResumePayload, resume_file


class AutomationPlatform(str, Enum):
    greenhouse = "greenhouse"
    workday = "workday"
    bayt = "bayt"


RUNNERS = {
    AutomationPlatform.greenhouse: greenhouse.run,
    AutomationPlatform.workday: workday.run,
    AutomationPlatform.bayt: bayt.run,
}


def run_automation(
    *,
    platform: AutomationPlatform,
    job_url: str,
    profile: Mapping[str, object],
    resume: Optional[Mapping[str, str]] = None,
    headless: bool = True,
) -> None:
    runner = RUNNERS[platform]
    resume_payload = None
    if resume and resume.get("content_b64"):
        resume_payload = ResumePayload(
            filename=resume.get("filename", "resume.pdf"),
            content_b64=resume["content_b64"],
        )

    with resume_file(resume_payload) as resume_path:
        runner(job_url, profile, resume_path, headless=headless)


def queue_job_automation(
    celery_app,
    *,
    platform: AutomationPlatform,
    job_url: str,
    profile: Mapping[str, object],
    resume: Optional[Mapping[str, str]] = None,
    notify_email: Optional[str] = None,
    notify_phone: Optional[str] = None,
) -> str:
    payload = {
        "platform": platform.value,
        "job_url": job_url,
        "profile": dict(profile),
        "resume": dict(resume) if resume else None,
        "notify_email": notify_email,
        "notify_phone": notify_phone,
    }
    result = celery_app.send_task("automation.run", args=[payload])
    return result.id
