from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from datetime import datetime
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # PostgreSQL Full Text Search vector
    search_vector = Column(TSVECTOR, nullable=True)

# GIN Index for Full Text Search
Index('project_search_idx', 'search_vector', postgresql_using='gin')
