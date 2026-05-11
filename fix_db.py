from sqlalchemy import text
from app.database import engine

def fix():
    with engine.connect() as conn:
        print("Checking for missing columns...")
        try:
            # Add trainer_id to clients
            conn.execute(text("ALTER TABLE clients ADD COLUMN IF NOT EXISTS trainer_id INTEGER REFERENCES trainers(id)"))
            conn.commit()
            print("Successfully checked/added trainer_id to clients table!")
        except Exception as e:
            print(f"Detail: {e}")

if __name__ == "__main__":
    fix()
