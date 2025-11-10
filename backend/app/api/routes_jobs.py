# backend/app/api/routes_jobs.py
from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..api.deps import get_current_user, require_db
from ..celery_app import celery_app
from ..models import Application, ApplicationStatus, User
from ..schemas import (
    JobAutomationRequest,
    JobAutomationResponse,
    JobFilters,
    JobOut,
    JobState,
)
from ..services.adapters import ADAPTERS
from ..services.automation.runner import AutomationPlatform, queue_job_automation

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _normalize_key(title: str | None, company: str | None) -> str:
    return f"{(title or '').strip().lower()}::{(company or '').strip().lower()}"


@router.post("/search", response_model=list[JobOut])
async def search_jobs(
    filters: JobFilters,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(require_db),
) -> list[JobOut]:
    user_apps = db.scalars(select(Application).where(Application.user_id == current_user.id)).all()
    state_map: Dict[str, JobState] = {}
    for app in user_apps:
        key = _normalize_key(app.title, app.company)
        if app.status == ApplicationStatus.draft:
            state_map[key] = JobState.saved
        else:
            state_map[key] = JobState.applied

    async def _fetch_from_adapter(
        adapter, query: str, location: str
    ) -> Iterable[Dict[str, Any]]:
        try:
            return await adapter.fetch(query=query, location=location)
        except Exception:  # pragma: no cover - adapter failure should not crash API
            return []

    query_text = filters.q or ""
    location = filters.location or "Dubai"
    tasks = [_fetch_from_adapter(adapter, query=query_text, location=location) for adapter in ADAPTERS]
    results_nested = await asyncio.gather(*tasks)

    jobs: list[JobOut] = []
    for adapter, items in zip(ADAPTERS, results_nested):
        for idx, item in enumerate(items or []):
            data = {**item}
            source = data.get("source") or adapter.source
            identifier = data.get("id") or data.get("apply_url") or f"{source}-{idx}"
            key = _normalize_key(data.get("title"), data.get("company"))
            state = state_map.get(key, JobState.recommended)
            job = JobOut(
                id=str(identifier),
                title=data.get("title") or "Untitled role",
                company=data.get("company") or "Unknown company",
                location=data.get("location"),
                salary_low=data.get("salary_low"),
                salary_high=data.get("salary_high"),
                currency=data.get("currency"),
                job_type=data.get("job_type"),
                experience_level=data.get("experience_level"),
                industry=data.get("industry"),
                education_level=data.get("education_level"),
                work_mode=data.get("work_mode"),
                posted_date=data.get("posted_date"),
                apply_url=data.get("apply_url"),
                description=data.get("description"),
                source=source,
                state=state,
            )
            jobs.append(job)

    return jobs


@router.post(
    "/run", response_model=JobAutomationResponse, status_code=status.HTTP_202_ACCEPTED
)
async def run_automation_job(
    payload: JobAutomationRequest,
    current_user: User = Depends(get_current_user),
) -> JobAutomationResponse:
    try:
        platform = AutomationPlatform(payload.platform)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    profile = payload.profile.model_dump(exclude_none=True)
    profile.setdefault("email", current_user.email)

    task_id = queue_job_automation(
        celery_app,
        platform=platform,
        job_url=str(payload.job_url),
        profile=profile,
        resume=payload.resume.model_dump() if payload.resume else None,
        notify_email=payload.notify_email or current_user.email,
        notify_phone=payload.notify_phone,
    )

    return JobAutomationResponse(task_id=task_id)
