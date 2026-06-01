from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional
import io
import csv
import json

from app.core.database import get_db
from app.core.security import verify_role, Roles, get_current_user
from app.models.finding import Finding
from app.models.secret_type import SecretType
from app.models.secret import Secret
from app.models.evidence import Evidence
from app.models.scan import Scan
from app.models.asset import Asset
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.finding import FindingResponse, FindingUpdate, FindingSearchResponse

router = APIRouter()

@router.get("", response_model=FindingSearchResponse, dependencies=[Depends(verify_role(Roles.ALL))])
def list_findings(
    project_id: Optional[int] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Finding, SecretType.name, Secret.masked_value, Evidence.content_snippet)\
        .join(SecretType, Finding.secret_type_id == SecretType.id)\
        .join(Secret, Secret.finding_id == Finding.id)\
        .join(Evidence, Evidence.finding_id == Finding.id)\
        .join(Scan, Finding.scan_id == Scan.id)\
        .join(Asset, Scan.asset_id == Asset.id)

    if project_id:
        query = query.filter(Asset.project_id == project_id)
    if severity:
        query = query.filter(Finding.severity == severity.upper())
    if status:
        query = query.filter(Finding.status == status.upper())

    if q:
        try:
            # PostgreSQL full text search vector match
            query = query.filter(Finding.search_vector.op("@@")(func.plainto_tsquery('english', q)))
        except Exception:
            # Fallback
            query = query.filter(Finding.file_path_or_url.ilike(f"%{q}%") | SecretType.name.ilike(f"%{q}%"))

    total = query.count()
    results = query.limit(limit).offset(offset).all()

    findings_resp = []
    for finding, type_name, masked_val, snippet in results:
        findings_resp.append(FindingResponse(
            id=finding.id,
            scan_id=finding.scan_id,
            secret_type_name=type_name,
            severity=finding.severity,
            status=finding.status,
            exposure_risk=finding.exposure_risk,
            compliance_risk=finding.compliance_risk,
            operational_risk=finding.operational_risk,
            risk_score=finding.risk_score,
            file_path_or_url=finding.file_path_or_url,
            line_number=finding.line_number,
            masked_value=masked_val,
            evidence_snippet=snippet,
            remediation_notes=finding.remediation_notes,
            owner_id=finding.owner_id,
            resolved_at=finding.resolved_at,
            created_at=finding.created_at
        ))

    return FindingSearchResponse(findings=findings_resp, total=total)

@router.patch("/{id}", response_model=FindingResponse)
def update_finding(
    id: int, 
    update: FindingUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(verify_role([Roles.ADMIN, Roles.ANALYST]))
):
    finding = db.query(Finding).filter(Finding.id == id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    old_status = finding.status
    finding.status = update.status.upper()
    
    if update.remediation_notes is not None:
        finding.remediation_notes = update.remediation_notes
        
    if update.owner_id is not None:
        finding.owner_id = update.owner_id

    # If resolved or closed, mark resolution time
    if finding.status in ["REMEDIATED", "CLOSED"] and old_status not in ["REMEDIATED", "CLOSED"]:
        finding.resolved_at = datetime.utcnow()
    elif finding.status not in ["REMEDIATED", "CLOSED"]:
        finding.resolved_at = None

    db.commit()

    # Get joined info for response mapping
    joined_info = db.query(SecretType.name, Secret.masked_value, Evidence.content_snippet)\
        .join(Secret, Secret.finding_id == Finding.id)\
        .join(Evidence, Evidence.finding_id == Finding.id)\
        .join(SecretType, Finding.secret_type_id == SecretType.id)\
        .filter(Finding.id == finding.id).first()

    type_name, masked_val, snippet = joined_info

    # Log action
    log = AuditLog(
        user_id=current_user.id,
        action="FINDING_UPDATE",
        details=f"Finding ID {finding.id} transitioned from {old_status} to {finding.status} by user {current_user.email}."
    )
    db.add(log)
    db.commit()

    return FindingResponse(
        id=finding.id,
        scan_id=finding.scan_id,
        secret_type_name=type_name,
        severity=finding.severity,
        status=finding.status,
        exposure_risk=finding.exposure_risk,
        compliance_risk=finding.compliance_risk,
        operational_risk=finding.operational_risk,
        risk_score=finding.risk_score,
        file_path_or_url=finding.file_path_or_url,
        line_number=finding.line_number,
        masked_value=masked_val,
        evidence_snippet=snippet,
        remediation_notes=finding.remediation_notes,
        owner_id=finding.owner_id,
        resolved_at=finding.resolved_at,
        created_at=finding.created_at
    )

@router.get("/export", dependencies=[Depends(verify_role(Roles.ALL))])
def export_audit_log(format: str = "json", db: Session = Depends(get_db)):
    """
    Exports findings in CSV or JSON format for audit/regulatory review.
    """
    findings_query = db.query(Finding, SecretType.name, Secret.masked_value)\
        .join(SecretType, Finding.secret_type_id == SecretType.id)\
        .join(Secret, Secret.finding_id == Finding.id).all()

    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Finding ID", "Secret Type", "Severity", "Status", "Risk Score", "File Path / URL", "Line", "Masked Value", "Created At"])
        for f, name, masked in findings_query:
            writer.writerow([f.id, name, f.severity, f.status, f.risk_score, f.file_path_or_url, f.line_number, masked, f.created_at.strftime("%Y-%m-%d %H:%M:%S")])
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=secretscope_audit_export_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
        )
    else:
        # Default JSON export
        export_list = []
        for f, name, masked in findings_query:
            export_list.append({
                "id": f.id,
                "secret_type": name,
                "severity": f.severity,
                "status": f.status,
                "risk_score": f.risk_score,
                "file_path_or_url": f.file_path_or_url,
                "line_number": f.line_number,
                "masked_value": masked,
                "created_at": f.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return StreamingResponse(
            io.BytesIO(json.dumps(export_list, indent=2).encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=secretscope_audit_export_{datetime.utcnow().strftime('%Y%m%d')}.json"}
        )
 Rama:
