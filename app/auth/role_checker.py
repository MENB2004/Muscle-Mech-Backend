from fastapi import Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.models.user_model import User

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        user_role = user.role.lower() if user.role else ""
        if user_role not in [r.lower() for r in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' not authorized for this resource. Required: {self.allowed_roles}"
            )
        return user
