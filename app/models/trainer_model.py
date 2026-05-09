from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Trainer(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    specialty = Column(String)
    experience = Column(String)
    rating = Column(Float, default=5.0)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="trainer_profile")

    @property
    def name(self):
        return self.user.name if self.user else ""

    @property
    def email(self):
        return self.user.email if self.user else ""
