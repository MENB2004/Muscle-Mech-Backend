from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnnouncementBase(BaseModel):
    title: str
    content: str
    type: str = "general"
    recipient_id: Optional[int] = None

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementResponse(AnnouncementBase):
    id: int
    sender_id: Optional[int] = None
    created_at: datetime
    sender_name: Optional[str] = None

    class Config:
        from_attributes = True
