from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.payment_model import Payment
from app.models.client_model import Client
from app.schemas.payment_schema import PaymentCreate, PaymentResponse
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Verify client exists
    client = db.query(Client).filter(Client.id == payment_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    # Check for duplicate payment for same month/year
    if payment_data.payment_type == "monthly":
        existing = db.query(Payment).filter(
            Payment.client_id == payment_data.client_id,
            Payment.billing_month == payment_data.billing_month,
            Payment.billing_year == payment_data.billing_year,
            Payment.payment_type == "monthly",
            Payment.status == "completed"
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Payment already recorded for this month")

    new_payment = Payment(**payment_data.dict(), created_by=current_user.id)
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    
    return new_payment

@router.get("/client/{client_id}", response_model=List[PaymentResponse])
def get_client_payments(client_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Payment).filter(Payment.client_id == client_id).order_by(Payment.payment_date.desc()).all()

@router.get("/year/{year}", response_model=List[PaymentResponse])
def get_payments_by_year(year: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Payment).filter(Payment.billing_year == year).order_by(Payment.payment_date.desc()).all()
