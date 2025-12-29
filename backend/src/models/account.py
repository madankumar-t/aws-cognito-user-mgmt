"""Account and pool related Pydantic models."""

from pydantic import BaseModel
from typing import Optional, List


class AccountResponse(BaseModel):
    """Response model for AWS account."""
    id: str
    name: str
    regions: List[str]


class PoolResponse(BaseModel):
    """Response model for Cognito User Pool."""
    id: str
    name: str
    creation_date: Optional[str] = None
    last_modified_date: Optional[str] = None

