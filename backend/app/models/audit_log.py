from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False) # e.g. "USER_LOGIN", "SCAN_START", "FINDING_REMEDIATED"
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(Text, nullable=True) # JSON or descriptive string of parameters changed
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
