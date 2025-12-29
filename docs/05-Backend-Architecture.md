# Backend Architecture & Folder Structure
## AWS Cognito User Management Application

**Document Version:** 1.0  
**Date:** 2024

---

## 1. Backend Folder Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── config.py                    # Configuration management
│   │
│   ├── middleware/                  # Request middleware
│   │   ├── __init__.py
│   │   ├── auth.py                 # JWT validation
│   │   ├── authorization.py        # RBAC enforcement
│   │   ├── logging.py              # Request logging
│   │   └── error_handler.py        # Global error handling
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── sts_service.py          # AWS STS AssumeRole
│   │   ├── cognito_service.py      # Cognito operations
│   │   ├── audit_service.py        # Audit logging
│   │   └── config_service.py       # Account/region config
│   │
│   ├── models/                      # Pydantic models
│   │   ├── __init__.py
│   │   ├── auth.py                 # Auth models
│   │   ├── user.py                 # User models
│   │   ├── account.py              # Account/pool models
│   │   └── common.py               # Common models
│   │
│   ├── routes/                      # API routes
│   │   ├── __init__.py
│   │   ├── auth.py                 # Auth endpoints
│   │   ├── accounts.py             # Account endpoints
│   │   ├── pools.py                # Pool endpoints
│   │   └── users.py                # User endpoints
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── exceptions.py           # Custom exceptions
│       ├── logger.py               # Logging setup
│       └── validators.py           # Input validation
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── unit/
│   │   ├── test_middleware.py
│   │   ├── test_services.py
│   │   └── test_routes.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_cognito.py
│   └── fixtures/
│       └── sample_data.py
│
├── lambda_handler.py                # AWS Lambda entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── sam-template.yaml                 # AWS SAM template
├── .gitignore
└── README.md
```

---

## 2. Component Descriptions

### 2.1 Main Application (`main.py`)

- FastAPI application instance
- Route registration
- Middleware registration
- Exception handlers
- CORS configuration

### 2.2 Configuration (`config.py`)

- Environment variable loading
- Configuration validation
- Default values
- Type-safe configuration class

### 2.3 Middleware Layer

**`auth.py`**: JWT token validation
- Validates Microsoft Entra ID JWT tokens
- Extracts user claims
- Verifies token signature using JWKS
- Checks token expiration

**`authorization.py`**: Role-based access control
- Checks user roles against required roles
- Enforces permissions per endpoint
- Returns 403 Forbidden if unauthorized

**`logging.py`**: Request/response logging
- Logs all incoming requests
- Logs responses
- Structured JSON logging
- Request ID tracking

**`error_handler.py`**: Global error handling
- Catches all exceptions
- Formats error responses
- Logs errors
- Returns appropriate HTTP status codes

### 2.4 Service Layer

**`sts_service.py`**: AWS STS operations
- AssumeRole for cross-account access
- Temporary credential management
- Credential caching
- Automatic credential refresh

**`cognito_service.py`**: Cognito User Pool operations
- List users (paginated)
- Get user details
- Create user
- Enable/disable user
- Set/reset password
- Force password reset
- List user pools

**`audit_service.py`**: Audit logging
- Logs all user management operations
- Tracks who did what, when
- Stores in CloudWatch Logs
- Structured audit trail

**`config_service.py`**: Configuration management
- Reads account mappings
- Manages region lists
- Role ARN construction

### 2.5 Models Layer

Pydantic models for:
- Request validation
- Response serialization
- Type safety
- API documentation (OpenAPI)

### 2.6 Routes Layer

FastAPI route handlers:
- `/auth/*` - Authentication endpoints
- `/accounts/*` - Account management
- `/pools/*` - Pool management
- `/users/*` - User management

---

## 3. Request Flow

```
1. API Gateway receives request
   ↓
2. Lambda function invoked
   ↓
3. FastAPI application processes request
   ↓
4. Logging Middleware: Log request
   ↓
5. Auth Middleware: Validate JWT token
   ↓
6. Authorization Middleware: Check roles
   ↓
7. Route Handler: Process business logic
   ↓
8. Service Layer: Execute operations
   ↓
9. Audit Service: Log operation
   ↓
10. Response returned to client
```

---

## 4. Dependencies

### 4.1 Core Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server (for local dev)
- `boto3` - AWS SDK
- `python-jose[cryptography]` - JWT validation
- `pydantic` - Data validation
- `python-dotenv` - Environment variables

### 4.2 Development Dependencies

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `moto` - AWS service mocking
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

---

## 5. Configuration Management

### 5.1 Environment Variables

```python
# config.py structure
class Settings:
    # Microsoft Entra ID
    entra_id_tenant_id: str
    entra_id_client_id: str
    entra_id_audience: str
    jwks_url: str
    
    # AWS
    account_role_name: str = "CognitoManagementRole"
    default_region: str = "us-east-1"
    
    # Application
    log_level: str = "INFO"
    allowed_origins: list[str]
    
    # Role Mapping
    admin_group_name: str = "cognito-admin"
    developer_group_name: str = "cognito-developer"
```

### 5.2 Account Configuration

Accounts can be configured via:
- Environment variables (comma-separated)
- AWS Systems Manager Parameter Store
- DynamoDB table (for complex scenarios)

---

## 6. Security Considerations

### 6.1 JWT Validation

- Signature verification using JWKS
- Expiration check
- Issuer validation
- Audience validation
- Token refresh handling

### 6.2 Credential Management

- No long-lived credentials
- Temporary credentials only (1 hour TTL)
- In-memory caching (never persisted)
- Automatic refresh before expiration

### 6.3 Input Validation

- Pydantic models validate all inputs
- SQL injection prevention (N/A - no SQL)
- XSS prevention (backend doesn't render HTML)
- Rate limiting via API Gateway

---

## 7. Error Handling Strategy

### 7.1 Exception Hierarchy

```
CognitoManagementException (base)
├── UnauthorizedException (401)
├── ForbiddenException (403)
├── NotFoundException (404)
├── ValidationException (400)
├── CognitoServiceException (500)
└── STSServiceException (500)
```

### 7.2 Error Response Format

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable message",
        "details": {}
    }
}
```

---

## 8. Logging Strategy

### 8.1 Log Levels

- **DEBUG**: Detailed diagnostic info
- **INFO**: General operational messages
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical failures

### 8.2 Structured Logging

All logs in JSON format:
```json
{
    "timestamp": "2024-01-01T12:00:00Z",
    "level": "INFO",
    "message": "User created",
    "context": {
        "operation": "create_user",
        "pool_id": "us-east-1_ABC123",
        "username": "john.doe",
        "user_id": "auth_user_id"
    }
}
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

- Test individual functions/methods
- Mock external dependencies (boto3, JWT)
- Target: 80%+ code coverage

### 9.2 Integration Tests

- Test API endpoints
- Use moto for AWS service mocking
- Test full request/response cycle

### 9.3 Test Organization

```
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Slower, end-to-end tests
└── fixtures/          # Reusable test data
```

---

## 10. Deployment

### 10.1 AWS SAM Template

- Lambda function definition
- API Gateway configuration
- IAM roles and policies
- Environment variables
- CloudWatch Logs

### 10.2 Build Process

1. Install dependencies
2. Run tests
3. Package Lambda function
4. Deploy via SAM CLI
5. Update API Gateway stage

---

**Document Control**

- **Version**: 1.0
- **Last Updated**: 2024

