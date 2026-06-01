from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ScanTrigger(BaseModel):
    asset_id: int

class ScanResponse(BaseModel):
    id: int
    asset_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    triggered_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True
