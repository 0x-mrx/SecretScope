from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AssetCreate(BaseModel):
    project_id: int
    type: str # WEBSITE, REPOSITORY, FILE_PATH
    target_url_or_path: str
    credentials: Optional[str] = None # Decrypted Git token, stored encrypted
    schedule_cron: Optional[str] = None # hourly, daily, weekly, None

class AssetResponse(BaseModel):
    id: int
    project_id: int
    type: str
    target_url_or_path: str
    schedule_cron: Optional[str] = None
    status: str
    last_scanned_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
