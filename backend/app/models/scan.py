from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="PENDING", nullable=False) # PENDING, RUNNING, COMPLETED, FAILED
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    triggered_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
