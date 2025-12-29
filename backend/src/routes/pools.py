"""Cognito User Pool management routes."""

from fastapi import APIRouter, Depends, Query
from typing import List
from src.models.account import PoolResponse
from src.middleware.auth import get_current_user
from src.middleware.authorization import require_roles
from src.services.sts_service import STSService
from src.services.cognito_service import CognitoService

router = APIRouter()
sts_service = STSService()


@router.get("/accounts/{account_id}/regions/{region}/pools", response_model=List[PoolResponse])
async def list_pools(
    account_id: str,
    region: str,
    current_user: dict = Depends(get_current_user),
    roles: List[str] = Depends(require_roles(["Admin", "Developer"]))
) -> List[PoolResponse]:
    """Lists Cognito User Pools in account/region."""
    # Assume role and get Cognito client
    credentials = await sts_service.assume_role(
        account_id=account_id,
        region=region,
        user_id=current_user["sub"]
    )
    cognito_client = sts_service.get_cognito_client(
        account_id=account_id,
        region=region,
        credentials=credentials
    )
    cognito_service = CognitoService(cognito_client)
    
    # List pools
    pools = await cognito_service.list_pools()
    
    return [PoolResponse(**pool) for pool in pools]

