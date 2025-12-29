"""Role-based authorization middleware."""

from fastapi import Depends, HTTPException, status
from typing import List
from src.middleware.auth import get_current_user


def require_roles(allowed_roles: List[str]):
    """Dependency factory for role-based authorization."""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_roles = current_user.get("roles", [])
        
        # Check if user has any of the required roles
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {allowed_roles}. User has: {user_roles}"
            )
        
        return user_roles
    
    return role_checker

