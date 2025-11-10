from __future__ import annotations

import os
from datetime import datetime

from celery import Celery, signals
from sqlalchemy.orm import Session

from .core.db import SessionLocal
from .models.metrics import Metric

# Load broker and result backend from environment variables
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)

celery_app = Celery(
    "wazifni",
    broker=broker_url,
    backend=result_backend,
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(["app.services.automation"])


@celery_app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return {"status": "debug task executed successfully"}


# Dictionary to track start times of tasks
_task_start_times: dict[str, datetime] = {}


@signals.task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    if task_id:
        _task_start_times[task_id] = datetime.utcnow()


@signals.task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, retval=None, state=None, **kwargs):
    if not task_id:
        return
    db: Session = SessionLocal()
    try:
        start = _task_start_times.pop(task_id, datetime.utcnow())
        duration = (datetime.utcnow() - start).total_seconds()
        metric = Metric(task_id=task_id, status=state or "unknown", duration=duration)
        db.add(metric)
        db.commit()
    finally:
        db.close()
