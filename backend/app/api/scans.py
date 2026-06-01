from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.core.database import get_db
from app.core.security import verify_role, Roles
from app.models.asset import Asset
from app.models.scan import Scan
from app.models.user import User
from app.schemas.scan import ScanTrigger, ScanResponse
from app.tasks.scanner_tasks import run_website_scan_task, run_repository_scan_task, run_directory_scan_task
from app.models.audit_log import AuditLog

router = APIRouter()

@router.post("/start", response_model=ScanResponse)
def trigger_scan(
    trigger: ScanTrigger, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))
):
    asset = db.query(Asset).filter(Asset.id == trigger.asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Create Scan entry
    scan = Scan(
        asset_id=asset.id,
        status="PENDING",
        started_at=datetime.utcnow(),
        triggered_by_user_id=current_user.id
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Queue worker tasks
    if asset.type == "WEBSITE":
        run_website_scan_task.delay(scan.id)
    elif asset.type == "REPOSITORY":
        run_repository_scan_task.delay(scan.id)
    elif asset.type == "FILE_PATH":
        run_directory_scan_task.delay(scan.id)

    # Log action
    log = AuditLog(
        user_id=current_user.id,
        action="SCAN_START",
        details=f"Scan ID {scan.id} started for asset {asset.target_url_or_path}"
    )
    db.add(log)
    db.commit()

    return scan

@router.post("/repository", response_model=ScanResponse)
def trigger_repository_scan(
    trigger: ScanTrigger, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))
):
    # Standard repository endpoint wrapper
    return trigger_scan(trigger, db, current_user)

@router.post("/assets", response_model=List[ScanResponse])
def trigger_bulk_scans(
    asset_ids: List[int], 
    db: Session = Depends(get_db), 
    current_user: User = Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))
):
    scans = []
    for asset_id in asset_ids:
        try:
            trig = ScanTrigger(asset_id=asset_id)
            scan = trigger_scan(trig, db, current_user)
            scans.append(scan)
        except Exception:  # nosec B112
            continue
    return scans
