from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime
from app.core.database import Base

class SecretType(Base):
    __tablename__ = "secret_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # e.g. "AWS_KEY", "OPENAI_KEY"
    pattern = Column(Text, nullable=False) # Regex pattern
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_custom = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
