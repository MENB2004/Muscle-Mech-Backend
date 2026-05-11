import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), ".")))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("--- Users ---")
    users = conn.execute(text("SELECT id, email, role FROM users")).fetchall()
    for u in users:
        print(u)
    
    print("\n--- Clients ---")
    clients = conn.execute(text("SELECT id, user_id, phone FROM clients")).fetchall()
    for c in clients:
        print(c)
