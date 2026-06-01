import json
from datetime import datetime
from celery import shared_task
from sqlalchemy import func
from app.core.database import SessionLocal
from app.core.encryption import encryptor
from app.services.scanner_engine import ScannerEngine
from app.services.risk_engine import RiskEngine
from app.services.report_generator import ReportGenerator

from app.models.scan import Scan
from app.models.scan_job import ScanJob
from app.models.asset import Asset
from app.models.finding import Finding
from app.models.secret import Secret
from app.models.evidence import Evidence
from app.models.secret_type import SecretType
from app.models.notification import Notification

@shared_task(bind=True)
def run_website_scan_task(self, scan_id: int):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return "Scan session not found"
        
        scan.status = "RUNNING"
        db.commit()

        # Track job
        job = ScanJob(
            scan_id=scan_id,
            celery_task_id=self.request.id,
            status="RUNNING"
        )
        db.add(job)
        db.commit()

        asset = db.query(Asset).filter(Asset.id == scan.asset_id).first()
        results = ScannerEngine.scan_website(asset.target_url_or_path, db)

        persist_findings(db, scan, asset, results)

        scan.status = "COMPLETED"
        scan.completed_at = datetime.utcnow()
        asset.last_scanned_at = datetime.utcnow()
        job.status = "SUCCESS"
        db.commit()

    except Exception as e:
        db.rollback()
        job = db.query(ScanJob).filter(ScanJob.celery_task_id == self.request.id).first()
        if job:
            job.status = "FAILURE"
            job.error_message = str(e)
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = "FAILED"
            scan.completed_at = datetime.utcnow()
        db.commit()
        raise e
    finally:
        db.close()

@shared_task(bind=True)
def run_repository_scan_task(self, scan_id: int):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return "Scan session not found"
        
        scan.status = "RUNNING"
        db.commit()

        job = ScanJob(
            scan_id=scan_id,
            celery_task_id=self.request.id,
            status="RUNNING"
        )
        db.add(job)
        db.commit()

        asset = db.query(Asset).filter(Asset.id == scan.asset_id).first()
        
        # Retrieve decrypted token if stored
        token = ""
        if asset.credentials_encrypted:
            try:
                token = encryptor.decrypt(asset.credentials_encrypted)
            except Exception:
                pass

        results = ScannerEngine.scan_git_repository(asset.target_url_or_path, token, db)

        persist_findings(db, scan, asset, results)

        scan.status = "COMPLETED"
        scan.completed_at = datetime.utcnow()
        asset.last_scanned_at = datetime.utcnow()
        job.status = "SUCCESS"
        db.commit()

    except Exception as e:
        db.rollback()
        job = db.query(ScanJob).filter(ScanJob.celery_task_id == self.request.id).first()
        if job:
            job.status = "FAILURE"
            job.error_message = str(e)
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = "FAILED"
            scan.completed_at = datetime.utcnow()
        db.commit()
        raise e
    finally:
        db.close()

@shared_task(bind=True)
def run_directory_scan_task(self, scan_id: int):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return "Scan session not found"
        
        scan.status = "RUNNING"
        db.commit()

        job = ScanJob(
            scan_id=scan_id,
            celery_task_id=self.request.id,
            status="RUNNING"
        )
        db.add(job)
        db.commit()

        asset = db.query(Asset).filter(Asset.id == scan.asset_id).first()
        results = ScannerEngine.scan_local_directory(asset.target_url_or_path, db)

        persist_findings(db, scan, asset, results)

        scan.status = "COMPLETED"
        scan.completed_at = datetime.utcnow()
        asset.last_scanned_at = datetime.utcnow()
        job.status = "SUCCESS"
        db.commit()

    except Exception as e:
        db.rollback()
        job = db.query(ScanJob).filter(ScanJob.celery_task_id == self.request.id).first()
        if job:
            job.status = "FAILURE"
            job.error_message = str(e)
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = "FAILED"
            scan.completed_at = datetime.utcnow()
        db.commit()
        raise e
    finally:
        db.close()

@shared_task
def generate_report_task(project_id: int, format_type: str, user_id: int = None):
    db = SessionLocal()
    try:
        ReportGenerator.build_and_store_report(project_id, format_type, db, user_id)
    finally:
        db.close()

def persist_findings(db: SessionLocal, scan: Scan, asset: Asset, scan_results: list):
    """
    Saves scan findings to the database, prevents duplicate files/hashes,
    adds risk scores, and updates FTS.
    """
    for r in scan_results:
        # Resolve Secret Type object
        secret_type_name = r["secret_type"]
        
        # Locate or create SecretType record
        stype = db.query(SecretType).filter(SecretType.name == secret_type_name).first()
        if not stype:
            # Create a placeholder rule
            stype = SecretType(
                name=secret_type_name,
                pattern=".*",
                description="Auto-generated scanner rule"
            )
            db.add(stype)
            db.commit()
            db.refresh(stype)

        # Apply Risk calculation
        risk_metrics = RiskEngine.calculate_risk(asset.type, secret_type_name, r["severity"])

        # Check for duplicates of the same secret value at the same location to keep DB clean
        encrypted_raw = encryptor.encrypt(r["match"])
        existing_secret = db.query(Secret).join(Finding).filter(
            Finding.file_path_or_url == r["file_path_or_url"],
            Finding.line_number == r["line"],
            Secret.masked_value == r["masked_value"]
        ).first()

        if existing_secret:
            # Already cataloged, skip
            continue

        # Save finding
        finding = Finding(
            scan_id=scan.id,
            secret_type_id=stype.id,
            severity=r["severity"],
            status="OPEN",
            exposure_risk=risk_metrics["exposure_risk"],
            compliance_risk=risk_metrics["compliance_risk"],
            operational_risk=risk_metrics["operational_risk"],
            risk_score=risk_metrics["risk_score"],
            file_path_or_url=r["file_path_or_url"],
            line_number=r["line"]
        )
        db.add(finding)
        db.commit()
        db.refresh(finding)

        # Update Full-Text Search vectors for Postgres
        try:
            # PostgreSQL specific full text update
            db.execute(
                func.update(Finding)
                .where(Finding.id == finding.id)
                .values(
                    search_vector=func.to_tsvector('english', f"{finding.file_path_or_url} {stype.name} {finding.severity}")
                )
            )
            db.commit()
        except Exception:
            # Fallback/ignore if not using PostgreSQL (e.g. testing)
            db.rollback()

        # Save secret details
        secret = Secret(
            finding_id=finding.id,
            confidence_score=r["confidence"],
            masked_value=r["masked_value"],
            encrypted_raw_value=encrypted_raw
        )
        db.add(secret)

        # Save evidence snippet
        evidence = Evidence(
            finding_id=finding.id,
            evidence_type="CODE_MATCH",
            content_snippet=r["context"],
            metadata_json=json.dumps(r.get("extra_metadata", {}))
        )
        db.add(evidence)
        db.commit()

        # Alert if critical / high finding
        if finding.severity in ["CRITICAL", "HIGH"]:
            notification = Notification(
                title=f"New {finding.severity} Secret Discovered!",
                message=f"A {secret_type_name} was exposed at {finding.file_path_or_url}:{finding.line_number}."
            )
            db.add(notification)
            db.commit()
