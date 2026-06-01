from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime
from app.core.database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False) # WEBSITE, REPOSITORY, FILE_PATH
    target_url_or_path = Column(String, nullable=False)
    
    # Encrypted credentials (e.g., git tokens, private keys)
    credentials_encrypted = Column(String, nullable=True)
    
    schedule_cron = Column(String, nullable=True) # Celery Beat cron schedule
    status = Column(String, default="ACTIVE", nullable=False) # ACTIVE, INACTIVE
    last_scanned_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # PostgreSQL Full Text Search vector
    search_vector = Column(TSVECTOR, nullable=True)

# GIN Index for Full Text Search
Index('asset_search_idx', 'search_vector', postgresql_using='gin')
