# app/services/ingest/scheduler.py
from sqlalchemy import select
from ...core.db import AsyncSessionLocal
from ...models import Job
from .adapters import ADAPTERS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def ingest_once():
    async with AsyncSessionLocal() as db:
        for adapter in ADAPTERS:
            for j in await adapter.fetch():
                exists = await db.execute(select(Job).where(
                    Job.title==j["title"], Job.company==j["company"], Job.apply_url==j["apply_url"]
                ))
               if exists.scalars().first():
                    continue

                db.add(Job(**j))
        await db.commit()

scheduler = AsyncIOScheduler()
def start_scheduler(interval_min: int=10):
    scheduler.add_job(ingest_once, "interval", minutes=interval_min, id="jobs_ingest", replace_existing=True)
    scheduler.start()
