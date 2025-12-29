"""User management routes."""

from fastapi import APIRouter, Depends, Query, Path
from typing import Optional, List
from src.models.user import (
    CreateUserRequest,
    CreateUserResponse,
    UserResponse,
    UserListResponse,
    SetPasswordRequest,
    UserStatusRequest
)
from src.middleware.auth import get_current_user
from src.middleware.authorization import require_roles
from src.services.sts_service import STSService
from src.services.cognito_service import CognitoService
from src.services.audit_service import AuditService

router = APIRouter()
sts_service = STSService()
audit_service = AuditService()


@router.get("/pools/{pool_id}/users", response_model=UserListResponse)
async def list_users(
    pool_id: str = Path(..., description="Cognito User Pool ID"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(60, ge=1, le=60, description="Items per page"),
    search: Optional[str] = Query(None, description="Search filter"),
    status: Optional[str] = Query(None, description="User status filter"),
    current_user: dict = Depends(get_current_user),
    roles: List[str] = Depends(require_roles(["Admin", "Developer"]))
):
    """List users in a Cognito User Pool."""
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
    
    # Build filter string
    filter_string = None
    if search:
        filter_string = f'username ^= "{search}"'
    if status:
        if filter_string:
            filter_string += f' AND status = "{status}"'
        else:
            filter_string = f'status = "{status}"'
    
    # List users
    result = await cognito_service.list_users(
        pool_id=pool_id,
        page_token=None,  # TODO: Implement pagination token handling
        limit=limit,
        filter_string=filter_string
    )
    
    # Audit log
    await audit_service.log_operation(
        user_id=current_user["sub"],
        operation="list_users",
        resource_type="cognito_user",
        resource_id=pool_id,
        account_id=account_id,
        region=region
    )
    
    return UserListResponse(
        users=[UserResponse(**user) for user in result["users"]],
        pagination={
            "page": page,
            "limit": limit,
            "total": result["count"],
            "next_token": result.get("pagination_token")
        }
    )


@router.post("/pools/{pool_id}/users", response_model=CreateUserResponse, status_code=201)
async def create_user(
    pool_id: str = Path(..., description="Cognito User Pool ID"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
    user_data: CreateUserRequest = ...,
    current_user: dict = Depends(get_current_user),
    roles: list = Depends(require_roles(["Admin"]))
):
    """Create a new user. Admin only."""
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
    
    # Create user
    user = await cognito_service.create_user(
        pool_id=pool_id,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        attributes=user_data.attributes,
        temporary_password=user_data.temporary_password
    )
    
    # Audit log
    await audit_service.log_operation(
        user_id=current_user["sub"],
        operation="create_user",
        resource_type="cognito_user",
        resource_id=user_data.username,
        account_id=account_id,
        region=region,
        details={"email": user_data.email}
    )
    
    return CreateUserResponse(user=UserResponse(**user), message="User created successfully")


@router.get("/pools/{pool_id}/users/{username}", response_model=UserResponse)
async def get_user(
    pool_id: str = Path(..., description="Cognito User Pool ID"),
    username: str = Path(..., description="Username"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
    current_user: dict = Depends(get_current_user),
    roles: List[str] = Depends(require_roles(["Admin", "Developer"]))
):
    """Get user details."""
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
    
    # Get user
    user = await cognito_service.get_user(pool_id, username)
    
    return UserResponse(**user)


@router.patch("/pools/{pool_id}/users/{username}/status", response_model=UserResponse)
async def update_user_status(
    pool_id: str = Path(..., description="Cognito User Pool ID"),
    username: str = Path(..., description="Username"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
    status: UserStatusRequest = ...,
    current_user: dict = Depends(get_current_user),
    roles: list = Depends(require_roles(["Admin"]))
):
    """Enable or disable a user. Admin only."""
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
    
    # Update status
    if status.enabled:
        user = await cognito_service.enable_user(pool_id, username)
    else:
        user = await cognito_service.disable_user(pool_id, username)
    
    # Audit log
    await audit_service.log_operation(
        user_id=current_user["sub"],
        operation="update_user_status",
        resource_type="cognito_user",
        resource_id=username,
        account_id=account_id,
        region=region,
        details={"enabled": status.enabled}
    )
    
    return UserResponse(**user)


@router.put("/pools/{pool_id}/users/{username}/password")
async def set_password(
    pool_id: str = Path(..., description="Cognito User Pool ID"),
    username: str = Path(..., description="Username"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
    password_data: SetPasswordRequest = ...,
    current_user: dict = Depends(get_current_user),
    roles: list = Depends(require_roles(["Admin"]))
):
    """Set user password. Admin only."""
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
    
    # Set password
    result = await cognito_service.set_password(
        pool_id=pool_id,
        username=username,
        password=password_data.password,
        permanent=password_data.permanent
    )
    
    # Audit log
    await audit_service.log_operation(
        user_id=current_user["sub"],
        operation="set_password",
        resource_type="cognito_user",
        resource_id=username,
        account_id=account_id,
        region=region
    )
    
    return result


@router.post("/pools/{pool_id}/users/{username}/reset-password")
async def reset_password(
    pool_id: str = Path(..., description="Cognito User Pool ID"),
    username: str = Path(..., description="Username"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
    current_user: dict = Depends(get_current_user),
    roles: list = Depends(require_roles(["Admin"]))
):
    """Send password reset email to user. Admin only."""
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
    
    # Reset password
    result = await cognito_service.reset_password(pool_id, username)
    
    # Audit log
    await audit_service.log_operation(
        user_id=current_user["sub"],
        operation="reset_password",
        resource_type="cognito_user",
        resource_id=username,
        account_id=account_id,
        region=region
    )
    
    return result


@router.post("/pools/{pool_id}/users/{username}/force-password-reset")
async def force_password_reset(
    pool_id: str = Path(..., description="Cognito User Pool ID"),
    username: str = Path(..., description="Username"),
    account_id: str = Query(..., description="AWS Account ID"),
    region: str = Query(..., description="AWS Region"),
    current_user: dict = Depends(get_current_user),
    roles: list = Depends(require_roles(["Admin"]))
):
    """Force user to reset password on next login. Admin only."""
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
    
    # Force password reset
    result = await cognito_service.force_password_reset(pool_id, username)
    
    # Audit log
    await audit_service.log_operation(
        user_id=current_user["sub"],
        operation="force_password_reset",
        resource_type="cognito_user",
        resource_id=username,
        account_id=account_id,
        region=region
    )
    
    return result

