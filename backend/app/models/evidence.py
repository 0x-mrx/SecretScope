from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.core.database import Base

class Evidence(Base):
    __tablename__ = "evidences"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String, nullable=False) # e.g. "SOURCE_MAP", "RAW_FILE_MATCH", "HTML_SCRIPT"
    content_snippet = Column(Text, nullable=False) # Context code line or surrounding lines
    metadata_json = Column(Text, nullable=True) # Storage location details or custom JSON fields
