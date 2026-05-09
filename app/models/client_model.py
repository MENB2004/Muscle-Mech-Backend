from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    phone = Column(String, nullable=True)
    goal = Column(String)
    join_date = Column(DateTime, default=datetime.utcnow)
    monthly_fee = Column(Float, default=2000.0)
    
    # Relationships
    user = relationship("User", back_populates="client_profile")

    @property
    def name(self):
        return self.user.name if self.user else ""
