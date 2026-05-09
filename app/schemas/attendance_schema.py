from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttendanceBase(BaseModel):
    client_id: int
    status: Optional[str] = "present"
    workout_type: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceResponse(AttendanceBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True
