from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentBase(BaseModel):
    client_id: int
    amount: float
    payment_type: Optional[str] = "monthly"
    billing_month: int
    billing_year: int
    status: Optional[str] = "completed"
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
