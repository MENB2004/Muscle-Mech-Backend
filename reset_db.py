import os
from app.database import engine, Base
from app.models.user_model import User
from app.models.trainer_model import Trainer
from app.models.client_model import Client
from app.models.attendance_model import Attendance
from app.models.payment_model import Payment
from app.models.communication_model import Announcement

# Diagnostic: Verify column exists in metadata
if 'must_change_password' not in User.__table__.columns:
    print("CRITICAL: 'must_change_password' NOT FOUND in User model metadata!")
    exit(1)
else:
    print("Metadata check: 'must_change_password' column found.")

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("Database reset successfully.")
