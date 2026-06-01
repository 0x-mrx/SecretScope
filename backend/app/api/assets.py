from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.core.security import verify_role, Roles
from app.core.encryption import encryptor
from app.models.asset import Asset
from app.models.project import Project
from app.schemas.asset import AssetCreate, AssetResponse
from app.models.audit_log import AuditLog

router = APIRouter()

@router.post("", response_model=AssetResponse, dependencies=[Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))])
def create_asset(asset_in: AssetCreate, db: Session = Depends(get_db)):
    # Verify project exists
    project = db.query(Project).filter(Project.id == asset_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    encrypted_creds = None
    if asset_in.credentials:
        encrypted_creds = encryptor.encrypt(asset_in.credentials)

    asset = Asset(
        project_id=asset_in.project_id,
        type=asset_in.type.upper(),
        target_url_or_path=asset_in.target_url_or_path,
        credentials_encrypted=encrypted_creds,
        schedule_cron=asset_in.schedule_cron,
        status="ACTIVE"
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    # Populate search vector for Postgres
    try:
        db.execute(
            func.update(Asset)
            .where(Asset.id == asset.id)
            .values(search_vector=func.to_tsvector('english', f"{asset.target_url_or_path} {asset.type}"))
        )
        db.commit()
    except Exception:
        db.rollback()

    # Log action
    log = AuditLog(
        action="ASSET_CREATE",
        details=f"Asset {asset.target_url_or_path} added to project {project.name}"
    )
    db.add(log)
    db.commit()

    return asset

@router.get("", response_model=List[AssetResponse], dependencies=[Depends(verify_role(Roles.ALL))])
def list_assets(project_id: Optional[int] = None, q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Asset)
    
    if project_id:
        query = query.filter(Asset.project_id == project_id)
        
    if q:
        try:
            query = query.filter(Asset.search_vector.op("@@")(func.plainto_tsquery('english', q)))
        except Exception:
            query = query.filter(Asset.target_url_or_path.ilike(f"%{q}%"))
            
    return query.all()
