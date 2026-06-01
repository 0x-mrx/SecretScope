from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReportGenerateRequest(BaseModel):
    project_id: int
    type: str # PDF, HTML, MD

class ReportResponse(BaseModel):
    id: int
    project_id: int
    type: str
    file_path: str
    summary_stats: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
