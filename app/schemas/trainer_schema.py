from pydantic import BaseModel, field_validator
from typing import Optional

class TrainerBase(BaseModel):
    specialty: Optional[str] = None
    experience: Optional[str] = None
    rating: Optional[float] = 5.0
    is_active: Optional[bool] = True

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: Optional[float]):
        if v is not None and (v < 0 or v > 5):
            raise ValueError('Rating must be between 0 and 5')
        return v

class TrainerUpdate(TrainerBase):
    pass

class TrainerResponse(TrainerBase):
    id: int
    user_id: int
    name: str # From User
    email: str # From User

    class Config:
        from_attributes = True
