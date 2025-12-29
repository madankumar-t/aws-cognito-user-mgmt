"""Authentication related Pydantic models."""

from pydantic import BaseModel
from typing import List, Optional


class UserInfoResponse(BaseModel):
    """Response model for current user information."""
    username: str
    email: Optional[str] = None
    name: Optional[str] = None
    roles: List[str]

