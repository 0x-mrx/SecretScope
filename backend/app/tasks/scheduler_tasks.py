from datetime import datetime, timedelta
from celery import shared_task
from app.core.database import SessionLocal
from app.models.asset import Asset
from app.models.scan import Scan
from app.tasks.scanner_tasks import run_website_scan_task, run_repository_scan_task, run_directory_scan_task

@shared_task
def run_scheduled_scans():
    """
    Checks active assets for schedules and spawns scan sessions.
    """
    db = SessionLocal()
    try:
        active_assets = db.query(Asset).filter(Asset.status == "ACTIVE").all()
        now = datetime.utcnow()

        for asset in active_assets:
            if not asset.schedule_cron:
                continue

            # Interpret schedule
            should_run = False
            last_run = asset.last_scanned_at or (now - timedelta(days=365))

            if asset.schedule_cron == "hourly" and (now - last_run) >= timedelta(hours=1):
                should_run = True
            elif asset.schedule_cron == "daily" and (now - last_run) >= timedelta(days=1):
                should_run = True
            elif asset.schedule_cron == "weekly" and (now - last_run) >= timedelta(weeks=1):
                should_run = True
            
            if should_run:
                # Trigger a new Scan entry
                scan = Scan(
                    asset_id=asset.id,
                    status="PENDING",
                    started_at=datetime.utcnow()
                )
                db.add(scan)
                db.commit()
                db.refresh(scan)

                # Queue the correct worker task
                if asset.type == "WEBSITE":
                    run_website_scan_task.delay(scan.id)
                elif asset.type == "REPOSITORY":
                    run_repository_scan_task.delay(scan.id)
                elif asset.type == "FILE_PATH":
                    run_directory_scan_task.delay(scan.id)

    finally:
        db.close()
