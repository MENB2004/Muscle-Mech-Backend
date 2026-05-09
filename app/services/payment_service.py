from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.payment_model import Payment
from app.models.client_model import Client

def get_client_fee_status(db: Session, client: Client):
    """
    Calculates dynamic fee status for a client based on the 10th of every month rule.
    """
    latest_payment = db.query(Payment).filter(
        Payment.client_id == client.id,
        Payment.payment_type == "monthly",
        Payment.status == "completed"
    ).order_by(Payment.billing_year.desc(), Payment.billing_month.desc()).first()

    today = datetime.utcnow().date()
    
    if latest_payment:
        owed_year = latest_payment.billing_year
        owed_month = latest_payment.billing_month + 1
        if owed_month > 12:
            owed_month = 1
            owed_year += 1
    else:
        join_date = client.join_date.date() if client.join_date else today
        owed_month = join_date.month
        owed_year = join_date.year

    next_due_date = datetime(owed_year, owed_month, 10).date()
    days_remaining = (next_due_date - today).days

    overdue_months = (today.year - owed_year) * 12 + today.month - owed_month
    if today.day > 10:
        overdue_months += 1

    if overdue_months >= 4:
        membership_status = "inactive"
    elif days_remaining < 0:
        membership_status = "overdue"
    elif (owed_year > today.year) or (owed_year == today.year and owed_month > today.month):
        # They have paid for the current calendar month
        membership_status = "active"
    else:
        # They owe for the current month, and it is on or before the 10th
        membership_status = "pending"

    return {
        "membership_status": membership_status,
        "next_due_date": next_due_date.isoformat(),
        "days_remaining": days_remaining
    }
