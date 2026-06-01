from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.core.database import Base

class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    celery_task_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="PENDING", nullable=False) # PENDING, RUNNING, SUCCESS, FAILURE
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
