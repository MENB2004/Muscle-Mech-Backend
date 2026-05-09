from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

from app.auth.dependencies import allow_admin, allow_staff, get_current_user
from app.models.user_model import User
from app.models.client_model import Client
from app.models.payment_model import Payment
from fastapi.responses import StreamingResponse
import io
import csv

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)



@router.get("/export/clients")
def export_clients(db: Session = Depends(get_db), current_user: User = Depends(allow_admin)):
    clients = db.query(Client).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Email", "Phone", "Join Date", "Monthly Fee"])
    
    for c in clients:
        writer.writerow([c.id, c.user.name, c.user.email, c.phone, c.join_date.isoformat(), c.monthly_fee])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=clients_export.csv"}
    )

@router.get("/export/payments")
def export_payments(db: Session = Depends(get_db), current_user: User = Depends(allow_admin)):
    payments = db.query(Payment).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Client Name", "Amount", "Month", "Year", "Date"])
    
    for p in payments:
        writer.writerow([p.id, p.client.user.name, p.amount, p.billing_month, p.billing_year, p.created_at.isoformat()])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=payments_export.csv"}
    )
