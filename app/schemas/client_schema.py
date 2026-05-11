from pydantic import BaseModel, EmailStr, field_validator
import re
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    goal: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    phone: Optional[str] = None
    monthly_fee: Optional[float] = 2000.0

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]):
        if v and v.strip():
            normalized = re.sub(r'[\s\-\+]', '', v)
            if not normalized.isdigit() or len(normalized) < 5 or len(normalized) > 15:
                raise ValueError('Phone must be between 5 and 15 digits')
            return normalized
        return None

    @field_validator('monthly_fee')
    @classmethod
    def validate_fee(cls, v: Optional[float]):
        if v is not None and v < 0:
            raise ValueError('Monthly fee cannot be negative')
        return v

class ClientCreate(ClientBase):
    user_id: int

class ClientWithUserCreate(ClientBase):
    name: str
    email: EmailStr
    password: str
    avatar_url: Optional[str] = None

class ClientUpdate(ClientBase):
    avatar_url: Optional[str] = None

class BulkFeeUpdate(BaseModel):
    new_fee: float

    @field_validator('new_fee')
    @classmethod
    def validate_fee(cls, v: float):
        if v < 0:
            raise ValueError('Monthly fee cannot be negative')
        return v

class ClientResponse(ClientBase):
    id: int
    user_id: int
    name: str # From User
    email: str # From User
    join_date: datetime
    
    # Dynamic fields from payment_service
    membership_status: Optional[str] = "active"
    next_due_date: Optional[str] = None
    days_remaining: Optional[int] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True
