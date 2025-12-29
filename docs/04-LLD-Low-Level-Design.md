# Low-Level Design (LLD)
## AWS Cognito User Management Application

**Document Version:** 1.0  
**Date:** 2024  
**Architect:** Principal Cloud Architect  
**Status:** Approved

---

## 1. Backend Architecture

### 1.1 Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT validation middleware
│   │   ├── authorization.py    # RBAC middleware
│   │   └── logging.py          # Request logging middleware
│   ├── services/
│   │   ├── __init__.py
│   │   ├── sts_service.py      # AWS STS AssumeRole service
│   │   ├── cognito_service.py  # Cognito user management
│   │   ├── audit_service.py    # Audit logging
│   │   └── config_service.py   # Account/region configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT token models
│   │   ├── user.py             # User request/response models
│   │   └── account.py          # Account/pool models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes
│   │   ├── accounts.py          # Account management routes
│   │   ├── pools.py             # Pool management routes
│   │   └── users.py             # User management routes
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py       # Custom exceptions
│       ├── logger.py           # Structured logging
│       └── validators.py       # Input validation
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── lambda_handler.py           # Lambda entry point
├── requirements.txt
└── sam-template.yaml           # AWS SAM template
```

### 1.2 Core Classes and Functions

#### 1.2.1 JWT Validation Middleware

```python
# middleware/auth.py

class JWTAuthMiddleware:
    """
    Validates JWT tokens from Microsoft Entra ID.
    """
    def __init__(self):
        self.jwks_client = None
        self.issuer = None
        self.audience = None
        
    async def validate_token(self, token: str) -> dict:
        """
        Validates JWT token and returns claims.
        Raises HTTPException if invalid.
        """
        # 1. Decode token header to get kid
        # 2. Fetch JWKS from Microsoft Entra ID
        # 3. Find matching key
        # 4. Verify signature
        # 5. Validate claims (iss, aud, exp, nbf)
        # 6. Return claims dict
        pass
    
    def extract_roles(self, claims: dict) -> list[str]:
        """
        Extracts roles from token groups claim.
        Maps Entra ID groups to app roles.
        """
        # Map groups to roles:
        # cognito-admin -> Admin
        # cognito-developer -> Developer
        pass
```

#### 1.2.2 STS Service

```python
# services/sts_service.py

class STSService:
    """
    Manages AWS STS AssumeRole operations and credential caching.
    """
    def __init__(self):
        self.credential_cache = {}  # In-memory cache
        self.sts_client = boto3.client('sts')
        
    async def assume_role(
        self, 
        account_id: str, 
        region: str,
        session_name: str
    ) -> dict:
        """
        Assumes IAM role in target account.
        Returns temporary credentials.
        """
        # 1. Check cache for existing credentials
        # 2. If expired or missing, call AssumeRole
        # 3. Cache credentials with TTL
        # 4. Return credentials dict
        pass
    
    def get_cognito_client(
        self, 
        account_id: str, 
        region: str,
        credentials: dict
    ) -> boto3.client:
        """
        Creates boto3 Cognito client with temporary credentials.
        """
        pass
    
    def _get_role_arn(self, account_id: str) -> str:
        """
        Constructs IAM role ARN for target account.
        Format: arn:aws:iam::{account_id}:role/CognitoManagementRole
        """
        pass
```

#### 1.2.3 Cognito Service

```python
# services/cognito_service.py

class CognitoService:
    """
    Abstraction layer for AWS Cognito User Pool operations.
    """
    def __init__(self, cognito_client: boto3.client):
        self.client = cognito_client
        
    async def list_users(
        self, 
        pool_id: str, 
        page_token: str = None,
        limit: int = 60
    ) -> dict:
        """
        Lists users in a Cognito User Pool.
        Returns paginated results.
        """
        pass
    
    async def get_user(self, pool_id: str, username: str) -> dict:
        """
        Retrieves detailed user information.
        """
        pass
    
    async def create_user(
        self, 
        pool_id: str, 
        username: str,
        email: str,
        password: str = None,
        attributes: dict = None,
        temporary_password: bool = False
    ) -> dict:
        """
        Creates a new user in Cognito User Pool.
        """
        pass
    
    async def enable_user(self, pool_id: str, username: str) -> dict:
        """
        Enables a disabled user.
        """
        pass
    
    async def disable_user(self, pool_id: str, username: str) -> dict:
        """
        Disables a user.
        """
        pass
    
    async def set_password(
        self, 
        pool_id: str, 
        username: str,
        password: str,
        permanent: bool = True
    ) -> dict:
        """
        Sets or resets user password.
        """
        pass
    
    async def force_password_reset(self, pool_id: str, username: str) -> dict:
        """
        Forces user to reset password on next login.
        """
        pass
    
    async def list_pools(self, region: str) -> list[dict]:
        """
        Lists all Cognito User Pools in a region.
        Note: Requires ListUserPools permission.
        """
        pass
```

### 1.3 API Route Specifications

#### 1.3.1 Authentication Routes

```python
# routes/auth.py

@router.get("/auth/me")
async def get_current_user(
    current_user: dict = Depends(get_current_user_dependency)
) -> dict:
    """
    Returns current authenticated user information.
    """
    return {
        "username": current_user["sub"],
        "email": current_user.get("email"),
        "roles": current_user.get("roles", [])
    }
```

#### 1.3.2 Account Routes

```python
# routes/accounts.py

@router.get("/accounts")
async def list_accounts(
    current_user: dict = Depends(get_current_user_dependency)
) -> list[dict]:
    """
    Lists AWS accounts user has access to.
    Reads from configuration or IAM role trust relationships.
    """
    pass

@router.post("/accounts/{account_id}/assume-role")
async def assume_role(
    account_id: str,
    region: str,
    current_user: dict = Depends(get_current_user_dependency)
) -> dict:
    """
    Assumes IAM role for target account.
    Returns temporary credentials (for internal use only).
    """
    pass
```

#### 1.3.3 Pool Routes

```python
# routes/pools.py

@router.get("/accounts/{account_id}/regions/{region}/pools")
async def list_pools(
    account_id: str,
    region: str,
    current_user: dict = Depends(get_current_user_dependency)
) -> list[dict]:
    """
    Lists Cognito User Pools in account/region.
    Requires Admin or Developer role.
    """
    pass
```

#### 1.3.4 User Routes

```python
# routes/users.py

@router.get("/pools/{pool_id}/users")
async def list_users(
    pool_id: str,
    account_id: str,
    region: str,
    page: int = 1,
    limit: int = 60,
    search: str = None,
    status: str = None,
    current_user: dict = Depends(get_current_user_dependency),
    roles: list[str] = Depends(require_roles(["Admin", "Developer"]))
) -> dict:
    """
    Lists users in a Cognito User Pool.
    Admin and Developer can access.
    """
    pass

@router.post("/pools/{pool_id}/users")
async def create_user(
    pool_id: str,
    account_id: str,
    region: str,
    user_data: CreateUserRequest,
    current_user: dict = Depends(get_current_user_dependency),
    roles: list[str] = Depends(require_roles(["Admin"]))
) -> dict:
    """
    Creates a new user.
    Admin only.
    """
    pass

@router.get("/pools/{pool_id}/users/{username}")
async def get_user(
    pool_id: str,
    username: str,
    account_id: str,
    region: str,
    current_user: dict = Depends(get_current_user_dependency),
    roles: list[str] = Depends(require_roles(["Admin", "Developer"]))
) -> dict:
    """
    Gets user details.
    Admin and Developer can access.
    """
    pass

@router.patch("/pools/{pool_id}/users/{username}/status")
async def update_user_status(
    pool_id: str,
    username: str,
    account_id: str,
    region: str,
    status: UserStatusRequest,
    current_user: dict = Depends(get_current_user_dependency),
    roles: list[str] = Depends(require_roles(["Admin"]))
) -> dict:
    """
    Enables or disables a user.
    Admin only.
    """
    pass

@router.put("/pools/{pool_id}/users/{username}/password")
async def set_password(
    pool_id: str,
    username: str,
    account_id: str,
    region: str,
    password_data: SetPasswordRequest,
    current_user: dict = Depends(get_current_user_dependency),
    roles: list[str] = Depends(require_roles(["Admin"]))
) -> dict:
    """
    Sets user password.
    Admin only.
    """
    pass

@router.post("/pools/{pool_id}/users/{username}/reset-password")
async def reset_password(
    pool_id: str,
    username: str,
    account_id: str,
    region: str,
    current_user: dict = Depends(get_current_user_dependency),
    roles: list[str] = Depends(require_roles(["Admin"]))
) -> dict:
    """
    Sends password reset email to user.
    Admin only.
    """
    pass

@router.post("/pools/{pool_id}/users/{username}/force-password-reset")
async def force_password_reset(
    pool_id: str,
    username: str,
    account_id: str,
    region: str,
    current_user: dict = Depends(get_current_user_dependency),
    roles: list[str] = Depends(require_roles(["Admin"]))
) -> dict:
    """
    Forces user to reset password on next login.
    Admin only.
    """
    pass
```

---

## 2. Frontend Architecture

### 2.1 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Home/login
│   │   ├── dashboard/
│   │   │   ├── page.tsx        # Main dashboard
│   │   │   ├── accounts/
│   │   │   │   └── page.tsx    # Account selection
│   │   │   ├── pools/
│   │   │   │   └── page.tsx    # Pool selection
│   │   │   └── users/
│   │   │       └── page.tsx    # User management
│   │   └── api/                # API routes (if needed)
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginButton.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── accounts/
│   │   │   ├── AccountList.tsx
│   │   │   ├── AccountCard.tsx
│   │   │   └── RegionSelector.tsx
│   │   ├── pools/
│   │   │   ├── PoolList.tsx
│   │   │   └── PoolCard.tsx
│   │   ├── users/
│   │   │   ├── UserList.tsx
│   │   │   ├── UserDetail.tsx
│   │   │   ├── CreateUserForm.tsx
│   │   │   └── UserActions.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── Toast.tsx
│   ├── lib/
│   │   ├── auth/
│   │   │   ├── msalConfig.ts
│   │   │   ├── msalInstance.ts
│   │   │   └── useAuth.ts
│   │   ├── api/
│   │   │   ├── client.ts        # Axios instance
│   │   │   ├── accounts.ts
│   │   │   ├── pools.ts
│   │   │   └── users.ts
│   │   └── utils/
│   │       ├── constants.ts
│   │       └── helpers.ts
│   ├── store/
│   │   ├── authStore.ts         # Auth state (Zustand)
│   │   ├── accountStore.ts      # Selected account/region/pool
│   │   └── userStore.ts         # User list state
│   ├── hooks/
│   │   ├── useAccounts.ts
│   │   ├── usePools.ts
│   │   └── useUsers.ts
│   └── types/
│       ├── auth.ts
│       ├── account.ts
│       ├── pool.ts
│       └── user.ts
├── public/
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

### 2.2 Key Components

#### 2.2.1 Authentication Hook

```typescript
// lib/auth/useAuth.ts

export function useAuth() {
  const msalInstance = useMsal();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [roles, setRoles] = useState<string[]>([]);
  
  const login = async () => {
    // MSAL login redirect
  };
  
  const logout = async () => {
    // MSAL logout
  };
  
  const getAccessToken = async () => {
    // Get JWT token from MSAL
  };
  
  return {
    isAuthenticated,
    user,
    roles,
    login,
    logout,
    getAccessToken
  };
}
```

#### 2.2.2 API Client

```typescript
// lib/api/client.ts

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor: Add JWT token
apiClient.interceptors.request.use(async (config) => {
  const token = await getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
    }
    return Promise.reject(error);
  }
);
```

#### 2.2.3 Account Selection Flow

```typescript
// components/accounts/AccountList.tsx

export function AccountList() {
  const { accounts, loading } = useAccounts();
  const { selectAccount } = useAccountStore();
  
  const handleSelect = (account: Account) => {
    selectAccount(account);
    router.push(`/dashboard/regions?account=${account.id}`);
  };
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {accounts.map(account => (
        <AccountCard
          key={account.id}
          account={account}
          onSelect={() => handleSelect(account)}
        />
      ))}
    </div>
  );
}
```

---

## 3. Database/Storage Design

### 3.1 Configuration Storage

**Option 1: Environment Variables**
- Account mappings stored in Lambda environment variables
- Simple, no external dependencies
- Limited flexibility

**Option 2: AWS Systems Manager Parameter Store**
- Account/region mappings stored as parameters
- Can be updated without code deployment
- Recommended for production

**Option 3: DynamoDB Table**
- More complex queries possible
- Better for large-scale deployments
- Additional cost

**Recommended**: Parameter Store for account mappings, environment variables for app config.

### 3.2 Credential Caching

- **Storage**: In-memory dictionary (per Lambda instance)
- **Key**: `{account_id}:{region}:{user_id}`
- **TTL**: 55 minutes (refresh before 1-hour expiration)
- **Eviction**: Automatic on Lambda instance termination

---

## 4. Error Handling

### 4.1 Backend Error Responses

```python
# utils/exceptions.py

class CognitoManagementException(Exception):
    """Base exception for Cognito management errors."""
    pass

class UnauthorizedException(CognitoManagementException):
    """401 Unauthorized"""
    pass

class ForbiddenException(CognitoManagementException):
    """403 Forbidden"""
    pass

class NotFoundException(CognitoManagementException):
    """404 Not Found"""
    pass

class ValidationException(CognitoManagementException):
    """400 Bad Request"""
    pass

# Error response format
{
    "error": {
        "code": "USER_NOT_FOUND",
        "message": "User 'john.doe' not found in pool",
        "details": {}
    }
}
```

### 4.2 Frontend Error Handling

- **Error Boundary**: Catch React errors
- **Toast Notifications**: User-friendly error messages
- **Retry Logic**: Automatic retry for transient failures
- **Fallback UI**: Graceful degradation

---

## 5. Logging Strategy

### 5.1 Structured Logging Format

```python
# utils/logger.py

logger.info(
    "user_operation",
    extra={
        "operation": "create_user",
        "pool_id": "us-east-1_ABC123",
        "username": "john.doe",
        "user_id": "auth_user_id",
        "account_id": "123456789012",
        "region": "us-east-1",
        "timestamp": "2024-01-01T12:00:00Z"
    }
)
```

### 5.2 Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning messages
- **ERROR**: Error conditions
- **CRITICAL**: Critical failures

### 5.3 Log Retention

- **CloudWatch Logs**: 30 days (default)
- **Long-term Storage**: Optional S3 export for compliance

---

## 6. Testing Strategy

### 6.1 Unit Tests

- **Coverage Target**: 80%+
- **Framework**: pytest
- **Mocking**: moto (AWS services), unittest.mock

### 6.2 Integration Tests

- **API Tests**: Test API endpoints with test Cognito pools
- **E2E Tests**: Full flow testing (optional)

### 6.3 Test Data

- **Fixtures**: Reusable test data
- **Test Pools**: Dedicated Cognito pools for testing
- **Cleanup**: Automatic cleanup after tests

---

## 7. Deployment Configuration

### 7.1 Environment Variables

```bash
# Backend Lambda
ENTRA_ID_TENANT_ID=...
ENTRA_ID_CLIENT_ID=...
ENTRA_ID_AUDIENCE=...
JWKS_URL=...
ALLOWED_ORIGINS=https://app.example.com
LOG_LEVEL=INFO
ACCOUNT_ROLE_NAME=CognitoManagementRole
```

### 7.2 IAM Role Configuration

See separate IAM policy document.

---

**Document Control**

- **Version**: 1.0
- **Last Updated**: 2024
- **Next Review**: Quarterly or on major changes

