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
from app.services.gemini_hunter import GeminiHunter
from app.services.gemini_exploit import GeminiExploiter

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

@router.post("/gemini/scan", dependencies=[Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))])
def trigger_gemini_scan(
    mode: int,
    target: str = None,
    file_content: str = None,
    current_user: User = Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))
):
    """
    Triggers specialized Gemini API Key Scanning based on Mode:
    - Mode 1: Single Domain
    - Mode 2: Batch Domains (content in file_content)
    - Mode 3: JS URL List (content in file_content)
    - Mode 4: Raw Keys (content in file_content or target)
    """
    hunter = GeminiHunter()
    
    if mode == 1:
        if not target:
            raise HTTPException(status_code=400, detail="Target URL is required for Mode 1")
        return hunter.run_single_domain_scan(target)
        
    elif mode == 2:
        if not file_content:
            raise HTTPException(status_code=400, detail="Domain list content is required for Mode 2")
        targets = file_content.splitlines()
        return hunter.run_batch_domains_scan(targets)
        
    elif mode == 3:
        if not file_content:
            raise HTTPException(status_code=400, detail="JS links content is required for Mode 3")
        js_links = file_content.splitlines()
        return hunter.run_js_list_scan(js_links)
        
    elif mode == 4:
        keys = []
        if target:
            keys.append(target)
        elif file_content:
            keys.extend(file_content.splitlines())
        else:
            raise HTTPException(status_code=400, detail="Target key or file_content containing keys is required for Mode 4")
        return hunter.run_raw_keys_validation(keys)
        
    else:
        raise HTTPException(status_code=400, detail="Invalid Gemini scan mode requested")

@router.post("/gemini/exploit", dependencies=[Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))])
def trigger_gemini_exploit(
    key: str,
    referer: str = None,
    current_user: User = Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))
):
    """
    Mode 5: Runs exhaustive capability check and exploitation tests on a given key.
    """
    if not key:
        raise HTTPException(status_code=400, detail="Key parameter is required for Mode 5 capability checks")
    return GeminiExploiter.scan_all_capabilities(key, referer)

