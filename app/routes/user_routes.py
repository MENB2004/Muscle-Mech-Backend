from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.schemas.user_schema import UserBase
from app.auth.dependencies import get_current_user
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

class UserUpdate(UserBase):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None # Should probably be restricted
    avatar_url: Optional[str] = None

@router.put("/me")
def update_me(user_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    data = user_data.dict(exclude_unset=True)
    
    # Don't allow changing role through this endpoint for safety
    if "role" in data:
        data.pop("role")
        
    for key, value in data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user
