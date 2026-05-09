from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.jwt_handler import decode_access_token
from app.models.user_model import User
from app.schemas.auth_schema import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    role: str = payload.get("role")
    if email is None:
        raise credentials_exception
        
    token_data = TokenData(email=email, role=role)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

from app.auth.role_checker import RoleChecker

allow_all = RoleChecker(["admin", "trainer", "client"])
allow_admin = RoleChecker(["admin"])
allow_staff = RoleChecker(["admin", "trainer"])
allow_trainer_or_admin = allow_staff
