from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.models.trainer_model import Trainer
from app.models.client_model import Client
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, PasswordChange
from app.schemas.auth_schema import Token
from app.auth.password_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_pwd = hash_password(user_data.password)
    
    # Create User
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pwd,
        role=user_data.role,
        avatar_url=user_data.avatar_url,
        must_change_password=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create sub-profile based on role
    if user_data.role == "trainer":
        new_trainer = Trainer(user_id=new_user.id)
        db.add(new_trainer)
    elif user_data.role == "client":
        new_client = Client(user_id=new_user.id)
        db.add(new_client)
    
    db.commit()
    return new_user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.role == "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client login is not supported."
        )
    
    # Create token
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password", response_model=UserResponse)
def change_password(data: PasswordChange, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.password = hash_password(data.new_password)
    current_user.must_change_password = False
    db.commit()
    db.refresh(current_user)
    return current_user
