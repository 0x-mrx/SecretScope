from celery import Celery
from app.core.config import settings

celery = Celery(
    "secretscope",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.scanner_tasks", "app.tasks.scheduler_tasks"]
)

celery.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    # Standard scheduler beat mapping
    beat_schedule={
        "check-scheduled-scans-every-minute": {
            "task": "app.tasks.scheduler_tasks.run_scheduled_scans",
            "schedule": 60.0, # run every 60 seconds
        }
    }
)
