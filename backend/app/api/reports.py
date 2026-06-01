from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import io
import mimetypes

from app.core.database import get_db
from app.core.security import verify_role, Roles, get_current_user
from app.models.report import Report
from app.models.project import Project
from app.models.user import User
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.tasks.scanner_tasks import generate_report_task
from app.services.storage_manager import storage_manager
from app.models.audit_log import AuditLog

router = APIRouter()

@router.post("/generate", response_model=dict)
def generate_report(
    req: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))
):
    project = db.query(Project).filter(Project.id == req.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Start Report generation Celery task
    generate_report_task.delay(req.project_id, req.type.upper(), current_user.id)

    # Log action
    log = AuditLog(
        user_id=current_user.id,
        action="REPORT_GENERATE",
        details=f"Triggered generating {req.type} report for project {project.name}"
    )
    db.add(log)
    db.commit()

    return {"message": f"Report generation task queued for project {project.name}"}

@router.get("", response_model=List[ReportResponse], dependencies=[Depends(verify_role(Roles.ALL))])
def list_reports(project_id: Optional[int] = None, q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Report)
    
    if project_id:
        query = query.filter(Report.project_id == project_id)
        
    if q:
        try:
            query = query.filter(Report.search_vector.op("@@")(func.plainto_tsquery('english', q)))
        except Exception:
            query = query.filter(Report.file_path.ilike(f"%{q}%") | Report.type.ilike(f"%{q}%"))
            
    return query.all()

@router.get("/download/{id}", dependencies=[Depends(verify_role(Roles.ALL))])
def download_report(id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report record not found")

    try:
        content_bytes = storage_manager.download_file(report.file_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch report from storage backend: {e}")

    filename = report.file_path.split("/")[-1]
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    return StreamingResponse(
        io.BytesIO(content_bytes),
        media_type=mime_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
