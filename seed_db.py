from app.database import engine, SessionLocal
from app.models.user_model import User
from app.models.trainer_model import Trainer
from app.models.client_model import Client
from app.auth.password_handler import hash_password

def seed():
    db = SessionLocal()
    try:
        # Check if users already exist
        if db.query(User).count() > 0:
            print("Database already has users. Skipping seed.")
            return

        print("Seeding demo accounts...")
        
        users = [
            {
                "name": "Alex Carter",
                "email": "admin@musclemech.com",
                "password": hash_password("23456789"),
                "role": "admin",
                "must_change_password": True
            },
            {
                "name": "Sam Rivera",
                "email": "trainer@musclemech.com",
                "password": hash_password("23456789"),
                "role": "trainer",
                "must_change_password": True
            },
            {
                "name": "Jordan Kim",
                "email": "client@musclemech.com",
                "password": hash_password("23456789"),
                "role": "client",
                "must_change_password": True
            },
            {
                "name": "Dummy Admin",
                "email": "dummy@musclemech.com",
                "password": hash_password("23456789"),
                "role": "admin",
                "must_change_password": True
            }
        ]

        for u in users:
            new_user = User(**u)
            db.add(new_user)
        
        db.commit()
        print("Seeding complete.")
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
