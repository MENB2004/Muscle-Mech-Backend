from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.database import get_db
from app.models.communication_model import Announcement
from app.schemas.communication_schema import AnnouncementCreate, AnnouncementResponse
from app.auth.dependencies import get_current_user, allow_trainer_or_admin
from app.models.user_model import User

router = APIRouter(
    prefix="/announcements",
    tags=["Communication"]
)

@router.post("/", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_announcement(data: AnnouncementCreate, db: Session = Depends(get_db), current_user: User = Depends(allow_trainer_or_admin)):
    new_msg = Announcement(**data.dict(), sender_id=current_user.id)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

@router.get("/me", response_model=List[AnnouncementResponse])
def get_my_announcements(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Fetch messages sent to this user OR broadcast messages (recipient_id is null)
    # Also include messages sent BY this user if they are staff
    query = db.query(Announcement).filter(
        or_(
            Announcement.recipient_id == current_user.id,
            Announcement.recipient_id == None
        )
    )
    
    messages = query.order_by(Announcement.created_at.desc()).all()
    
    for m in messages:
        m.sender_name = m.sender.name if m.sender else "System"
        
    return messages
