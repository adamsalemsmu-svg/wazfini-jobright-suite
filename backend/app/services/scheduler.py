# backend/app/services/ingest/scheduler.py

from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ...core.db import AsyncSessionLocal
from ...models import Job
from .adapters import ADAPTERS


async def ingest_once() -> None:
    """Fetch jobs from all adapters and upsert new ones."""
    async with AsyncSessionLocal() as db:
        for adapter in ADAPTERS:
            jobs = await adapter.fetch()

            for j in jobs:
                # does a job with same title/company/url already exist?
                exists = await db.execute(
                    select(Job).where(
                        Job.title == j["title"],
                        Job.company == j["company"],
                        Job.apply_url == j["apply_url"],
                    )
                )

                if exists.scalars().first():
                    continue

                db.add(Job(**j))

        await db.commit()


# a single scheduler instance for the process
scheduler = AsyncIOScheduler()


def start_scheduler(interval_min: int = 10) -> None:
    """
    Start/refresh the ingest job on an interval.
    If the job already exists, it will be replaced.
    """
    scheduler.add_job(
        ingest_once,
        trigger="interval",
        minutes=interval_min,
        id="jobs_ingest",
        replace_existing=True,
    )
    scheduler.start()
