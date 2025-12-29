# Example FastAPI Code Snippets
## AWS Cognito User Management Application

**Document Version:** 1.0  
**Date:** 2024

---

## 1. Main Application (`main.py`)

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.middleware.auth import JWTAuthMiddleware
from src.middleware.authorization import require_roles
from src.middleware.logging import LoggingMiddleware
from src.middleware.error_handler import error_handler
from src.routes import auth, accounts, pools, users
from src.config import settings
from src.utils.logger import get_logger
from src.utils.exceptions import CognitoManagementException

logger = get_logger(__name__)

app = FastAPI(
    title="AWS Cognito User Management API",
    description="Enterprise-grade Cognito user management with Microsoft Entra ID authentication",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.middleware("http")(LoggingMiddleware())
app.middleware("http")(JWTAuthMiddleware())

# Global Exception Handler
app.exception_handler(CognitoManagementException)(error_handler)

# Include Routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(accounts.router, prefix="/api/v1", tags=["Accounts"])
app.include_router(pools.router, prefix="/api/v1", tags=["Pools"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AWS Cognito User Management API"}

# Lambda Handler
def lambda_handler(event, context):
    """AWS Lambda handler for API Gateway."""
    from mangum import Mangum
    handler = Mangum(app)
    return handler(event, context)
```

---

## 2. Configuration (`config.py`)

```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Microsoft Entra ID Configuration
    entra_id_tenant_id: str
    entra_id_client_id: str
    entra_id_audience: str
    jwks_url: str = None  # Auto-constructed if not provided
    
    # AWS Configuration
    account_role_name: str = "CognitoManagementRole"
    default_region: str = "us-east-1"
    
    # Application Configuration
    log_level: str = "INFO"
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # Role Mapping
    admin_group_name: str = "cognito-admin"
    developer_group_name: str = "cognito-developer"
    
    # Account Configuration (comma-separated or from Parameter Store)
    accounts_config_source: str = "env"  # "env" | "ssm" | "dynamodb"
    accounts_env_var: str = "ALLOWED_ACCOUNTS"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-construct JWKS URL if not provided
        if not self.jwks_url:
            self.jwks_url = (
                f"https://login.microsoftonline.com/"
                f"{self.entra_id_tenant_id}/discovery/v2.0/keys"
            )

settings = Settings()
```

---

## 3. JWT Authentication Middleware (`middleware/auth.py`)

```python
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from jose.utils import base64url_decode
import httpx
import json
from typing import Dict, List, Optional
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
security = HTTPBearer()

class JWTAuthMiddleware:
    """Middleware for JWT token validation."""
    
    def __init__(self):
        self.jwks_cache = {}
        self.role_mapping = {
            settings.admin_group_name: "Admin",
            settings.developer_group_name: "Developer"
        }
    
    async def __call__(self, request: Request, call_next):
        """Validate JWT token for protected routes."""
        # Skip auth for health check and public routes
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = authorization.split(" ")[1]
        
        try:
            # Validate token and extract claims
            claims = await self.validate_token(token)
            
            # Extract roles
            roles = self.extract_roles(claims)
            
            # Attach user info to request state
            request.state.user = {
                "sub": claims.get("sub"),
                "email": claims.get("email"),
                "name": claims.get("name"),
                "roles": roles,
                "claims": claims
            }
            
            logger.info(
                "user_authenticated",
                extra={
                    "user_id": claims.get("sub"),
                    "email": claims.get("email"),
                    "roles": roles
                }
            )
            
        except JWTError as e:
            logger.warning("jwt_validation_failed", extra={"error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return await call_next(request)
    
    async def validate_token(self, token: str) -> Dict:
        """Validate JWT token and return claims."""
        # Decode token header to get key ID
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        
        # Get signing key from JWKS
        signing_key = await self.get_signing_key(kid)
        
        # Verify and decode token
        try:
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=settings.entra_id_audience,
                issuer=f"https://login.microsoftonline.com/{settings.entra_id_tenant_id}/v2.0"
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTClaimsError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
        
        return claims
    
    async def get_signing_key(self, kid: str) -> str:
        """Get signing key from JWKS endpoint."""
        # Check cache first
        if kid in self.jwks_cache:
            return self.jwks_cache[kid]
        
        # Fetch JWKS
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.jwks_url)
            response.raise_for_status()
            jwks = response.json()
        
        # Find matching key
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Construct RSA public key
                from cryptography.hazmat.primitives.asymmetric import rsa
                from cryptography.hazmat.primitives import serialization
                import base64
                
                n = base64.urlsafe_b64decode(key["n"] + "==")
                e = base64.urlsafe_b64decode(key["e"] + "==")
                
                public_key = rsa.RSAPublicNumbers(
                    int.from_bytes(e, "big"),
                    int.from_bytes(n, "big")
                ).public_key()
                
                pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                self.jwks_cache[kid] = pem.decode("utf-8")
                return self.jwks_cache[kid]
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signing key not found"
        )
    
    def extract_roles(self, claims: Dict) -> List[str]:
        """Extract roles from token groups claim."""
        groups = claims.get("groups", [])
        roles = []
        
        for group in groups:
            if group in self.role_mapping:
                roles.append(self.role_mapping[group])
        
        return roles

# Dependency for getting current user
async def get_current_user(request: Request) -> Dict:
    """Dependency to get current authenticated user."""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return request.state.user
```

---

## 4. Authorization Middleware (`middleware/authorization.py`)

```python
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
```

---

## 5. STS Service (`services/sts_service.py`)

```python
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Optional
from datetime import datetime, timedelta
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class STSService:
    """Service for AWS STS AssumeRole operations."""
    
    def __init__(self):
        self.sts_client = boto3.client("sts")
        self.credential_cache: Dict[str, Dict] = {}
        self.cache_ttl = timedelta(minutes=55)  # Refresh before 1-hour expiration
    
    async def assume_role(
        self,
        account_id: str,
        region: str,
        user_id: str
    ) -> Dict:
        """
        Assume IAM role in target account.
        Returns temporary credentials with caching.
        """
        cache_key = f"{account_id}:{region}:{user_id}"
        
        # Check cache
        if cache_key in self.credential_cache:
            cached = self.credential_cache[cache_key]
            if datetime.now() < cached["expires_at"]:
                logger.debug("using_cached_credentials", extra={"account_id": account_id})
                return cached["credentials"]
        
        # Assume role
        role_arn = self._get_role_arn(account_id)
        session_name = f"CognitoManagement-{user_id[:32]}"  # Max 64 chars
        
        try:
            response = self.sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=3600  # 1 hour
            )
            
            credentials = response["Credentials"]
            expires_at = datetime.now() + timedelta(seconds=credentials["Expiration"].timestamp() - datetime.now().timestamp())
            
            # Cache credentials
            self.credential_cache[cache_key] = {
                "credentials": {
                    "AccessKeyId": credentials["AccessKeyId"],
                    "SecretAccessKey": credentials["SecretAccessKey"],
                    "SessionToken": credentials["SessionToken"]
                },
                "expires_at": expires_at
            }
            
            logger.info(
                "role_assumed",
                extra={
                    "account_id": account_id,
                    "role_arn": role_arn,
                    "session_name": session_name
                }
            )
            
            return self.credential_cache[cache_key]["credentials"]
            
        except ClientError as e:
            logger.error(
                "assume_role_failed",
                extra={
                    "account_id": account_id,
                    "error": str(e)
                }
            )
            raise Exception(f"Failed to assume role: {str(e)}")
    
    def get_cognito_client(
        self,
        account_id: str,
        region: str,
        credentials: Dict
    ) -> boto3.client:
        """Create boto3 Cognito client with temporary credentials."""
        return boto3.client(
            "cognito-idp",
            region_name=region,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )
    
    def _get_role_arn(self, account_id: str) -> str:
        """Construct IAM role ARN for target account."""
        return f"arn:aws:iam::{account_id}:role/{settings.account_role_name}"
```

---

## 6. Cognito Service (`services/cognito_service.py`)

```python
import boto3
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
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "ResourceNotFoundException":
                raise NotFoundException(f"User pool {pool_id} not found")
            raise CognitoServiceException(f"Failed to list users: {str(e)}")
    
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
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "UserNotFoundException":
                raise NotFoundException(f"User {username} not found")
            raise CognitoServiceException(f"Failed to get user: {str(e)}")
    
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
                params["TemporaryPassword"] = password if temporary_password else None
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
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "UsernameExistsException":
                raise ValidationException(f"User {username} already exists")
            raise CognitoServiceException(f"Failed to create user: {str(e)}")
    
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
            raise CognitoServiceException(f"Failed to enable user: {str(e)}")
    
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
            raise CognitoServiceException(f"Failed to disable user: {str(e)}")
    
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
            raise CognitoServiceException(f"Failed to set password: {str(e)}")
    
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
            raise CognitoServiceException(f"Failed to reset password: {str(e)}")
    
    async def force_password_reset(self, pool_id: str, username: str) -> Dict:
        """Force user to reset password on next login."""
        try:
            # Set user status to FORCE_CHANGE_PASSWORD
            self.client.admin_set_user_password(
                UserPoolId=pool_id,
                Username=username,
                Password="TempPassword123!",  # Temporary password
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
            raise CognitoServiceException(f"Failed to force password reset: {str(e)}")
    
    async def list_pools(self) -> List[Dict]:
        """List all Cognito User Pools in the region."""
        try:
            response = self.client.list_user_pools(MaxResults=60)
            
            pools = []
            for pool in response.get("UserPools", []):
                pools.append({
                    "id": pool["Id"],
                    "name": pool["Name"],
                    "creation_date": pool["CreationDate"].isoformat(),
                    "last_modified_date": pool["LastModifiedDate"].isoformat()
                })
            
            logger.info("pools_listed", extra={"count": len(pools)})
            
            return pools
            
        except ClientError as e:
            raise CognitoServiceException(f"Failed to list pools: {str(e)}")
    
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
            "mfa_enabled": user_data.get("MFAOptions", []) != []
        }
```

---

## 7. User Routes (`routes/users.py`)

```python
from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
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
from src.utils.logger import get_logger

logger = get_logger(__name__)
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
    roles: list = Depends(require_roles(["Admin", "Developer"]))
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
    
    # Calculate pagination
    page_token = None  # In real implementation, decode from page number
    
    # List users
    result = await cognito_service.list_users(
        pool_id=pool_id,
        page_token=page_token,
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
    
    return {
        "users": result["users"],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": result["count"],
            "next_token": result.get("pagination_token")
        }
    }

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
    
    return {"user": user, "message": "User created successfully"}

# Additional routes follow similar pattern...
```

---

**Document Control**

- **Version**: 1.0
- **Last Updated**: 2024

