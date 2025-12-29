"""AWS Cognito service for user management."""

import boto3
import secrets
import string
from botocore.exceptions import ClientError
from typing import Dict, List, Optional
from src.utils.logger import get_logger
from src.utils.exceptions import (
    CognitoServiceException,
    NotFoundException,
    ValidationException
)

logger = get_logger(__name__)


class CognitoService:
    """Service for AWS Cognito User Pool operations."""
    
    def __init__(self, cognito_client: boto3.client):
        self.client = cognito_client
    
    async def list_users(
        self,
        pool_id: str,
        page_token: Optional[str] = None,
        limit: int = 60,
        filter_string: Optional[str] = None
    ) -> Dict:
        """List users in a Cognito User Pool."""
        try:
            params = {
                "UserPoolId": pool_id,
                "Limit": limit
            }
            
            if page_token:
                params["PaginationToken"] = page_token
            
            if filter_string:
                params["Filter"] = filter_string
            
            response = self.client.list_users(**params)
            
            users = []
            for user in response.get("Users", []):
                users.append(self._format_user(user))
            
            result = {
                "users": users,
                "pagination_token": response.get("PaginationToken"),
                "count": len(users)
            }
            
            logger.info(
                "users_listed",
                extra={
                    "pool_id": pool_id,
                    "count": len(users)
                }
            )
            
            return result
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "ResourceNotFoundException":
                raise NotFoundException(f"User pool {pool_id} not found")
            logger.error("list_users_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to list users: {error_code}")
    
    async def get_user(self, pool_id: str, username: str) -> Dict:
        """Get detailed user information."""
        try:
            response = self.client.admin_get_user(
                UserPoolId=pool_id,
                Username=username
            )
            
            user = self._format_user(response)
            
            logger.info(
                "user_retrieved",
                extra={
                    "pool_id": pool_id,
                    "username": username
                }
            )
            
            return user
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "UserNotFoundException":
                raise NotFoundException(f"User {username} not found")
            logger.error("get_user_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to get user: {error_code}")
    
    async def create_user(
        self,
        pool_id: str,
        username: str,
        email: str,
        password: Optional[str] = None,
        attributes: Optional[Dict] = None,
        temporary_password: bool = False
    ) -> Dict:
        """Create a new user in Cognito User Pool."""
        try:
            user_attributes = [
                {"Name": "email", "Value": email}
            ]
            
            if attributes:
                for key, value in attributes.items():
                    user_attributes.append({"Name": key, "Value": str(value)})
            
            params = {
                "UserPoolId": pool_id,
                "Username": username,
                "UserAttributes": user_attributes,
                "MessageAction": "SUPPRESS"  # Don't send welcome email
            }
            
            if password:
                if temporary_password:
                    params["TemporaryPassword"] = password
                else:
                    params["TemporaryPassword"] = password
                    params["MessageAction"] = "SUPPRESS"
            
            response = self.client.admin_create_user(**params)
            
            user = self._format_user(response["User"])
            
            logger.info(
                "user_created",
                extra={
                    "pool_id": pool_id,
                    "username": username,
                    "email": email
                }
            )
            
            return user
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "UsernameExistsException":
                raise ValidationException(f"User {username} already exists")
            logger.error("create_user_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to create user: {error_code}")
    
    async def enable_user(self, pool_id: str, username: str) -> Dict:
        """Enable a disabled user."""
        try:
            self.client.admin_enable_user(
                UserPoolId=pool_id,
                Username=username
            )
            
            logger.info(
                "user_enabled",
                extra={
                    "pool_id": pool_id,
                    "username": username
                }
            )
            
            return await self.get_user(pool_id, username)
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error("enable_user_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to enable user: {error_code}")
    
    async def disable_user(self, pool_id: str, username: str) -> Dict:
        """Disable a user."""
        try:
            self.client.admin_disable_user(
                UserPoolId=pool_id,
                Username=username
            )
            
            logger.info(
                "user_disabled",
                extra={
                    "pool_id": pool_id,
                    "username": username
                }
            )
            
            return await self.get_user(pool_id, username)
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error("disable_user_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to disable user: {error_code}")
    
    async def set_password(
        self,
        pool_id: str,
        username: str,
        password: str,
        permanent: bool = True
    ) -> Dict:
        """Set or reset user password."""
        try:
            self.client.admin_set_user_password(
                UserPoolId=pool_id,
                Username=username,
                Password=password,
                Permanent=permanent
            )
            
            logger.info(
                "password_set",
                extra={
                    "pool_id": pool_id,
                    "username": username,
                    "permanent": permanent
                }
            )
            
            return {"message": "Password set successfully"}
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error("set_password_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to set password: {error_code}")
    
    async def reset_password(self, pool_id: str, username: str) -> Dict:
        """Send password reset email to user."""
        try:
            self.client.admin_reset_user_password(
                UserPoolId=pool_id,
                Username=username
            )
            
            logger.info(
                "password_reset_initiated",
                extra={
                    "pool_id": pool_id,
                    "username": username
                }
            )
            
            return {"message": "Password reset email sent"}
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error("reset_password_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to reset password: {error_code}")
    
    async def force_password_reset(self, pool_id: str, username: str) -> Dict:
        """Force user to reset password on next login."""
        try:
            # Generate a temporary password
            temp_password = ''.join(
                secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*")
                for _ in range(16)
            )
            
            # Set temporary password
            self.client.admin_set_user_password(
                UserPoolId=pool_id,
                Username=username,
                Password=temp_password,
                Permanent=False
            )
            
            logger.info(
                "force_password_reset_set",
                extra={
                    "pool_id": pool_id,
                    "username": username
                }
            )
            
            return {"message": "User will be forced to reset password on next login"}
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error("force_password_reset_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to force password reset: {error_code}")
    
    async def list_pools(self) -> List[Dict]:
        """List all Cognito User Pools in the region."""
        try:
            response = self.client.list_user_pools(MaxResults=60)
            
            pools = []
            for pool in response.get("UserPools", []):
                pools.append({
                    "id": pool["Id"],
                    "name": pool["Name"],
                    "creation_date": pool["CreationDate"].isoformat() if pool.get("CreationDate") else None,
                    "last_modified_date": pool["LastModifiedDate"].isoformat() if pool.get("LastModifiedDate") else None
                })
            
            logger.info("pools_listed", extra={"count": len(pools)})
            
            return pools
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error("list_pools_failed", extra={"error": str(e)})
            raise CognitoServiceException(f"Failed to list pools: {error_code}")
    
    def _format_user(self, user_data: Dict) -> Dict:
        """Format Cognito user data to standard format."""
        attributes = {}
        for attr in user_data.get("Attributes", []):
            attributes[attr["Name"]] = attr["Value"]
        
        return {
            "username": user_data.get("Username"),
            "user_status": user_data.get("UserStatus"),
            "enabled": user_data.get("Enabled", False),
            "user_create_date": user_data.get("UserCreateDate").isoformat() if user_data.get("UserCreateDate") else None,
            "user_last_modified_date": user_data.get("UserLastModifiedDate").isoformat() if user_data.get("UserLastModifiedDate") else None,
            "attributes": attributes,
            "mfa_enabled": len(user_data.get("MFAOptions", [])) > 0
        }

