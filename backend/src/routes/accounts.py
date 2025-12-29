"""Account management routes."""

from fastapi import APIRouter, Depends
from typing import List
from src.models.account import AccountResponse
from src.middleware.auth import get_current_user
from src.services.config_service import ConfigService

router = APIRouter()
config_service = ConfigService()


@router.get("/accounts", response_model=List[AccountResponse])
async def list_accounts(
    current_user: dict = Depends(get_current_user)
) -> List[AccountResponse]:
    """Lists AWS accounts user has access to."""
    accounts = config_service.get_accounts()
    return [AccountResponse(**account) for account in accounts]

