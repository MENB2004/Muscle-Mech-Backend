from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine, Base

from app.models.user_model import User
from app.models.trainer_model import Trainer
from app.models.client_model import Client
from app.routes import auth_routes, client_routes, trainer_routes, payment_routes, communication_routes, analytics_routes, user_routes

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "https://muscle-mech-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(client_routes.router)
app.include_router(trainer_routes.router)
app.include_router(payment_routes.router)
app.include_router(communication_routes.router)
app.include_router(analytics_routes.router)
app.include_router(user_routes.router)

@app.get("/")
def root():
    return {"message": "Muscle Mech Backend Running"}

@app.get("/db-test")
def db_test():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        return {"database": "connected"}