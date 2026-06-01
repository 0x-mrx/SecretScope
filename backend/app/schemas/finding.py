from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FindingUpdate(BaseModel):
    status: str # OPEN, INVESTIGATING, CONFIRMED, REMEDIATED, CLOSED
    remediation_notes: Optional[str] = None
    owner_id: Optional[int] = None

class FindingResponse(BaseModel):
    id: int
    scan_id: int
    secret_type_name: str
    severity: str
    status: str
    exposure_risk: str
    compliance_risk: str
    operational_risk: str
    risk_score: float
    file_path_or_url: str
    line_number: Optional[int] = None
    masked_value: str
    evidence_snippet: Optional[str] = None
    remediation_notes: Optional[str] = None
    owner_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
class FindingSearchResponse(BaseModel):
    findings: list[FindingResponse]
    total: int
