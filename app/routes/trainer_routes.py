from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.trainer_model import Trainer
from app.schemas.trainer_schema import TrainerUpdate, TrainerResponse
from app.auth.role_checker import RoleChecker
from app.auth.dependencies import get_current_user
from app.models.user_model import User
from app.models.client_model import Client
from app.models.payment_model import Payment
from app.models.communication_model import Announcement

allow_admin = RoleChecker(["admin"])
allow_staff = RoleChecker(["admin", "trainer"])

router = APIRouter(
    prefix="/trainers",
    tags=["Trainers"]
)

@router.get("/", response_model=List[TrainerResponse])
def get_trainers(db: Session = Depends(get_db), current_user: User = Depends(allow_admin)):
    trainers = db.query(Trainer).all()
    return trainers

@router.get("/me", response_model=TrainerResponse)
def get_my_trainer_profile(db: Session = Depends(get_db), current_user: User = Depends(allow_staff)):
    trainer = db.query(Trainer).filter(Trainer.user_id == current_user.id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer profile not found")
    return trainer

@router.get("/{trainer_id}", response_model=TrainerResponse)
def get_trainer(trainer_id: int, db: Session = Depends(get_db), current_user: User = Depends(allow_staff)):
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Permission check: Trainers can only see their own profile
    if current_user.role == "trainer" and trainer.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this trainer")
    
    return trainer

@router.put("/{trainer_id}", response_model=TrainerResponse)
def update_trainer(trainer_id: int, trainer_data: TrainerUpdate, db: Session = Depends(get_db), current_user: User = Depends(allow_staff)):
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    # Permission: Trainer can only update their own profile
    if current_user.role == "trainer" and trainer.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this trainer")
    
    data = trainer_data.dict(exclude_unset=True)
    
    # Security: Only admins can change is_active or rating
    if current_user.role != "admin":
        data.pop("is_active", None)
        data.pop("rating", None)

    for key, value in data.items():
        setattr(trainer, key, value)
    
    db.commit()
    db.refresh(trainer)
    return trainer

@router.delete("/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trainer(trainer_id: int, db: Session = Depends(get_db), current_user: User = Depends(allow_admin)):
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    user_id = trainer.user_id
    
    db.query(Client).filter(Client.trainer_id == trainer_id).update(
        {Client.trainer_id: None},
        synchronize_session=False
    )
    if user_id:
        db.query(Payment).filter(Payment.created_by == user_id).update(
            {Payment.created_by: None},
            synchronize_session=False
        )
        # Handle announcements sent by this trainer
        db.query(Announcement).filter(Announcement.sender_id == user_id).update(
            {Announcement.sender_id: None},
            synchronize_session=False
        )
        # Handle announcements received by this trainer (if any)
        db.query(Announcement).filter(Announcement.recipient_id == user_id).update(
            {Announcement.recipient_id: None},
            synchronize_session=False
        )
        user = db.query(User).filter(User.id == user_id).first()
        db.delete(trainer)
        if user:
            db.delete(user)
    else:
        db.delete(trainer)
            
    db.commit()
    return None
