from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    amount = Column(Float, nullable=False)
    payment_type = Column(String, default="monthly") # admission, monthly, personal_training, other
    billing_month = Column(Integer, nullable=False)
    billing_year = Column(Integer, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed") # completed, pending, failed
    notes = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    client = relationship("Client")
    creator = relationship("User")
