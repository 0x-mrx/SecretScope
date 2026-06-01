from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.core.database import Base

class Secret(Base):
    __tablename__ = "secrets"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)
    
    # Masked value (e.g., AKIA************1234)
    masked_value = Column(String, nullable=False)
    
    # Fully encrypted raw secret value
    encrypted_raw_value = Column(String, nullable=False)
