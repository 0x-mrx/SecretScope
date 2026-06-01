from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.core.security import verify_role, Roles
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse
from app.models.audit_log import AuditLog

router = APIRouter()

@router.post("", response_model=ProjectResponse, dependencies=[Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))])
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    # Check duplicate
    existing = db.query(Project).filter(Project.name == project_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project with this name already exists")

    project = Project(
        name=project_in.name,
        description=project_in.description
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Populate search vector for Postgres
    try:
        db.execute(
            func.update(Project)
            .where(Project.id == project.id)
            .values(search_vector=func.to_tsvector('english', f"{project.name} {project.description or ''}"))
        )
        db.commit()
    except Exception:
        db.rollback()

    # Log action
    log = AuditLog(
        action="PROJECT_CREATE",
        details=f"Project {project.name} created."
    )
    db.add(log)
    db.commit()

    return project

@router.get("", response_model=List[ProjectResponse], dependencies=[Depends(verify_role(Roles.ALL))])
def list_projects(q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Project)
    if q:
        try:
            # PostgreSQL full text search vector match
            query = query.filter(Project.search_vector.op("@@")(func.plainto_tsquery('english', q)))
        except Exception:
            # Fallback to simple ILIKE matching
            query = query.filter(Project.name.ilike(f"%{q}%") | Project.description.ilike(f"%{q}%"))
    return query.all()
