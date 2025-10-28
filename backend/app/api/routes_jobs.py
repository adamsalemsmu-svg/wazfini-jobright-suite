# backend/app/api/routes_jobs.py
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlmodel import select

from ..core.db import get_session
from ..models import Job
from ..schemas import JobFilters, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/search", response_model=list[JobOut])
async def search_jobs(filters: JobFilters, db=Depends(get_session)):
    q = select(Job)

    if filters.location:
        q = q.where(Job.location.ilike(f"%{filters.location}%"))

    if filters.industry:
        q = q.where(Job.industry.ilike(f"%{filters.industry}%"))

    if filters.experience_level:
        q = q.where(Job.experience_level == filters.experience_level)

    if filters.job_type:
        q = q.where(Job.job_type == filters.job_type)

    if filters.education_level:
        q = q.where(Job.education_level == filters.education_level)

    if filters.work_mode:
        q = q.where(Job.work_mode == filters.work_mode)

    if filters.salary_min is not None:
        q = q.where(Job.salary_low >= filters.salary_min)

    if filters.salary_max is not None:
        q = q.where(Job.salary_high <= filters.salary_max)

    if filters.posted_within_days:
        cutoff = datetime.utcnow() - timedelta(days=filters.posted_within_days)
        q = q.where(Job.posted_date >= cutoff)

    if filters.q:
        q = q.where(
            or_(
                Job.title.ilike(f"%{filters.q}%"),
                Job.description.ilike(f"%{filters.q}%"),
            )
        )

    q = q.order_by(Job.posted_date.desc())
    res = (await db.execute(q)).scalars().all()
    return res
