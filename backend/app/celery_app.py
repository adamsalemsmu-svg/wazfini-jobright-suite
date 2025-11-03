from celery import Celery
import os

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


@celery_app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return {"status": "debug task executed successfully"}
