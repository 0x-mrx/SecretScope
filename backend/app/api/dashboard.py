from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.core.database import get_db
from app.core.security import verify_role, Roles
from app.models.finding import Finding
from app.models.asset import Asset
from app.models.project import Project

router = APIRouter()

@router.get("", dependencies=[Depends(verify_role(Roles.ALL))])
def get_executive_dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    # 1. Findings by Severity
    severity_stats = db.query(
        Finding.severity, 
        func.count(Finding.id)
    ).group_by(Finding.severity).all()
    
    severity_map = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for sev, count in severity_stats:
        severity_map[sev.upper()] = count

    # 2. Assets by Risk & Type
    asset_stats = db.query(
        Asset.type,
        func.count(Asset.id)
    ).group_by(Asset.type).all()
    
    asset_map = {"WEBSITE": 0, "REPOSITORY": 0, "FILE_PATH": 0, "TOTAL": 0}
    total_assets = 0
    for atype, count in asset_stats:
        asset_map[atype.upper()] = count
        total_assets += count
    asset_map["TOTAL"] = total_assets

    # 3. Mean Time To Remediate (MTTR)
    # Average time in hours between created_at and resolved_at for resolved findings
    remediated_findings = db.query(Finding).filter(
        Finding.status.in_(["REMEDIATED", "CLOSED"]),
        Finding.resolved_at != None
    ).all()
    
    mttr_hours = 0.0
    if remediated_findings:
        total_time = sum((f.resolved_at - f.created_at).total_seconds() for f in remediated_findings)
        mttr_hours = round((total_time / len(remediated_findings)) / 3600.0, 1)

    # 4. SLA Compliance Metrics
    # Target SLA: CRITICAL <= 24h, HIGH <= 72h, MEDIUM <= 168h (7 days), LOW <= 720h (30 days)
    total_sla_eligible = len(remediated_findings)
    sla_compliant_count = 0
    
    for f in remediated_findings:
        resolution_time = f.resolved_at - f.created_at
        if f.severity == "CRITICAL" and resolution_time <= timedelta(hours=24):
            sla_compliant_count += 1
        elif f.severity == "HIGH" and resolution_time <= timedelta(hours=72):
            sla_compliant_count += 1
        elif f.severity == "MEDIUM" and resolution_time <= timedelta(days=7):
            sla_compliant_count += 1
        elif f.severity == "LOW" and resolution_time <= timedelta(days=30):
            sla_compliant_count += 1
            
    sla_percentage = 100.0
    if total_sla_eligible > 0:
        sla_percentage = round((sla_compliant_count / total_sla_eligible) * 100.0, 1)

    # 5. Open Findings Trend (Last 7 days)
    trend = []
    now = datetime.utcnow()
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        
        count = db.query(func.count(Finding.id)).filter(
            Finding.created_at <= day_end,
            Finding.status != "CLOSED",
            Finding.status != "REMEDIATED"
        ).scalar()
        
        trend.append({
            "date": day.strftime("%Y-%m-%d"),
            "count": count
        })

    # Recent Audit Log Activity
    from app.models.audit_log import AuditLog
    recent_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(5).all()
    activity = []
    for log in recent_logs:
        activity.append({
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "severity_distribution": severity_map,
        "asset_metrics": asset_map,
        "mttr_hours": mttr_hours,
        "sla_compliance_percentage": sla_percentage,
        "open_findings_trend": trend,
        "recent_activity": activity
    }
