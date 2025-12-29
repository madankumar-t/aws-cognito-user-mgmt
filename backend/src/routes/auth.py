"""Authentication routes."""

from fastapi import APIRouter, Depends
from src.models.auth import UserInfoResponse
from src.middleware.auth import get_current_user

router = APIRouter()


@router.get("/auth/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
) -> UserInfoResponse:
    """Returns current authenticated user information."""
    return UserInfoResponse(
        username=current_user.get("sub", ""),
        email=current_user.get("email"),
        name=current_user.get("name"),
        roles=current_user.get("roles", [])
    )

