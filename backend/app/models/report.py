from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime
from app.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False) # PDF, HTML, MD
    file_path = Column(String, nullable=False) # Local path or MinIO key
    generated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    summary_stats = Column(Text, nullable=True) # JSON summary (total secrets, severities, etc.)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # PostgreSQL Full Text Search vector
    search_vector = Column(TSVECTOR, nullable=True)

# GIN Index for Full Text Search
Index('report_search_idx', 'search_vector', postgresql_using='gin')
