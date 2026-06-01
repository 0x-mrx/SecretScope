from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Index, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime
from app.core.database import Base

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    secret_type_id = Column(Integer, ForeignKey("secret_types.id", ondelete="RESTRICT"), nullable=False)
    
    severity = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String, default="OPEN", nullable=False) # OPEN, INVESTIGATING, CONFIRMED, REMEDIATED, CLOSED
    
    # Risk Engine metrics
    exposure_risk = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    compliance_risk = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    operational_risk = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Float, default=0.0, nullable=False) # numeric score e.g., 0-100
    
    file_path_or_url = Column(String, nullable=False)
    line_number = Column(Integer, nullable=True)
    
    # Owner & Remediation tracker
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remediation_notes = Column(Text, nullable=True)
    
    # Audit timestamps
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # PostgreSQL Full Text Search vector
    search_vector = Column(TSVECTOR, nullable=True)

# GIN Index for Full Text Search
Index('finding_search_idx', 'search_vector', postgresql_using='gin')
