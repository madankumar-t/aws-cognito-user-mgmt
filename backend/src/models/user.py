"""User-related Pydantic models."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    username: str = Field(..., min_length=1, max_length=128, description="Username")
    email: EmailStr = Field(..., description="User email address")
    password: Optional[str] = Field(None, min_length=8, description="User password")
    attributes: Optional[Dict[str, str]] = Field(None, description="Additional user attributes")
    temporary_password: bool = Field(False, description="Whether password is temporary")


class UserResponse(BaseModel):
    """Response model for user data."""
    username: str
    user_status: str
    enabled: bool
    user_create_date: Optional[str] = None
    user_last_modified_date: Optional[str] = None
    attributes: Dict[str, Any]
    mfa_enabled: bool


class CreateUserResponse(BaseModel):
    """Response model for user creation."""
    user: UserResponse
    message: str


class UserListResponse(BaseModel):
    """Response model for user list."""
    users: List[UserResponse]
    pagination: Dict[str, Any]


class SetPasswordRequest(BaseModel):
    """Request model for setting password."""
    password: str = Field(..., min_length=8, description="New password")
    permanent: bool = Field(True, description="Whether password is permanent")


class UserStatusRequest(BaseModel):
    """Request model for updating user status."""
    enabled: bool = Field(..., description="Whether user should be enabled")

