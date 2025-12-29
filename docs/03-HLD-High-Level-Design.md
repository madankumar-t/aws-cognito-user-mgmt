# High-Level Design (HLD)
## AWS Cognito User Management Application

**Document Version:** 1.0  
**Date:** 2024  
**Architect:** Principal Cloud Architect  
**Status:** Approved

---

## 1. System Overview

### 1.1 Architecture Pattern

The application follows a **serverless microservices architecture** with:
- **Frontend**: Next.js SPA deployed on AWS S3 + CloudFront
- **Backend**: FastAPI on AWS Lambda with API Gateway
- **Authentication**: Microsoft Entra ID (Azure AD) OIDC/OAuth2
- **Authorization**: Role-based access control (RBAC) with JWT claims
- **Multi-Account Access**: AWS STS AssumeRole for temporary credentials

### 1.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Next.js SPA (React)                              │   │
│  │  - MSAL Authentication                                    │   │
│  │  - Role-based UI Components                              │   │
│  │  - Account/Region/Pool Selection                         │   │
│  │  - User Management Interface                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         AWS API Gateway HTTP API                          │   │
│  │  - Request Routing                                        │   │
│  │  - Rate Limiting                                          │   │
│  │  - CORS Configuration                                     │   │
│  │  - WAF Integration                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         AWS Lambda Functions (FastAPI)                    │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │  Authentication Middleware                         │   │   │
│  │  │  - JWT Validation                                  │   │   │
│  │  │  - Role Extraction                                 │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │  Authorization Middleware                          │   │   │
│  │  │  - RBAC Enforcement                                │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │  API Routes                                         │   │   │
│  │  │  - Account Management                               │   │   │
│  │  │  - Pool Management                                  │   │   │
│  │  │  - User Management                                  │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │  STS Service │  │ Cognito      │  │ Audit      │    │   │
│  │  │  - AssumeRole│  │ Service      │  │ Service    │    │   │
│  │  │  - Temp Creds│  │ - User CRUD  │  │ - Logging  │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS SERVICES LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  AWS STS     │  │  Cognito     │  │  CloudWatch  │         │
│  │  (Multi-Acct)│  │  User Pools  │  │  Logs        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Microsoft Entra ID (Azure AD)                           │   │
│  │  - OIDC/OAuth2 Provider                                  │   │
│  │  - JWT Token Issuance                                    │   │
│  │  - Group Membership                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Components

**Authentication Module:**
- MSAL Provider wrapper
- Auth context/state management
- Token refresh logic
- Protected route wrapper

**Account Selection Module:**
- Account list component
- Account selection handler
- Region selector
- Pool selector

**User Management Module:**
- User list table
- User detail view
- Create user form
- Action buttons (role-aware)

**Common Components:**
- Layout (Header, Sidebar, Footer)
- Loading states
- Error boundaries
- Toast notifications

### 2.2 Backend Components

**API Layer:**
- FastAPI application
- Route handlers
- Request/response models
- Error handlers

**Middleware Layer:**
- JWT validation middleware
- Role authorization middleware
- Request logging middleware
- Error handling middleware

**Service Layer:**
- STS Service (AssumeRole, credential management)
- Cognito Service (user CRUD operations)
- Audit Service (operation logging)
- Configuration Service (account/region mapping)

**Data Layer:**
- AWS SDK (boto3) clients
- Temporary credential cache
- Configuration storage

---

## 3. Data Flow

### 3.1 Authentication Flow

```
1. User → Frontend: Click "Sign In"
2. Frontend → Entra ID: Redirect to OAuth2 authorization endpoint
3. User → Entra ID: Enter credentials
4. Entra ID → Frontend: Authorization code (redirect)
5. Frontend → Entra ID: Exchange code for JWT token
6. Frontend: Store JWT token securely
7. Frontend → Backend: API request with JWT in Authorization header
8. Backend: Validate JWT (signature, expiration, issuer)
9. Backend: Extract roles from token claims
10. Backend: Process request with role context
```

### 3.2 Multi-Account Access Flow

```
1. User selects AWS account
2. Frontend → Backend: GET /api/v1/accounts/{account_id}/assume-role
3. Backend → AWS STS: AssumeRole with account-specific IAM role ARN
4. AWS STS → Backend: Temporary credentials (AccessKey, SecretKey, SessionToken)
5. Backend: Cache credentials (in-memory, TTL: 55 minutes)
6. Backend → AWS Cognito: List pools using temporary credentials
7. Backend → Frontend: Return pool list
8. User selects pool
9. Subsequent requests use cached credentials for that account
```

### 3.3 User Management Flow (Example: Create User)

```
1. Admin user fills create user form
2. Frontend → Backend: POST /api/v1/pools/{pool_id}/users
   Headers: Authorization: Bearer <JWT>
   Body: {username, email, password, attributes}
3. Backend Middleware: Validate JWT, extract role
4. Backend Middleware: Check role = "Admin" (authorization)
5. Backend Service: Get cached STS credentials for account
6. Backend Service: Create boto3 Cognito client with temp credentials
7. Backend Service → AWS Cognito: admin_create_user()
8. Backend Service: Log operation to CloudWatch
9. Backend → Frontend: 201 Created with user object
10. Frontend: Show success message, refresh user list
```

---

## 4. Security Architecture

### 4.1 Authentication Security

- **JWT Validation**: Verify signature using Microsoft Entra ID public keys (JWKS)
- **Token Expiration**: Tokens expire after 1 hour, refresh token used for renewal
- **HTTPS Only**: All communications encrypted in transit
- **Secure Storage**: JWT stored in httpOnly cookies or secure localStorage

### 4.2 Authorization Security

- **Role-Based Access Control**: Enforced at both frontend and backend
- **Least Privilege**: IAM roles have minimum required permissions
- **Backend Validation**: Frontend role checks are for UX only; backend always validates

### 4.3 Credential Security

- **No Long-Lived Credentials**: All AWS access via STS AssumeRole
- **Temporary Credentials**: Maximum 1-hour TTL
- **Credential Caching**: In-memory only, never persisted
- **Automatic Refresh**: Credentials refreshed before expiration

### 4.4 Network Security

- **API Gateway**: WAF rules for DDoS protection
- **VPC Endpoints**: Optional private connectivity to AWS services
- **CORS**: Restricted to known frontend origins
- **Rate Limiting**: Per-user and per-IP limits

---

## 5. Scalability Design

### 5.1 Horizontal Scaling

- **Lambda**: Auto-scales based on request volume
- **API Gateway**: Handles traffic spikes automatically
- **Frontend**: Served via CloudFront CDN globally

### 5.2 Performance Optimization

- **Credential Caching**: Reduces STS calls
- **Connection Pooling**: Reuse boto3 clients
- **Pagination**: Large result sets paginated
- **Async Operations**: FastAPI async/await for I/O

### 5.3 Capacity Planning

- **Expected Load**: 100 concurrent users
- **Peak Load**: 200 concurrent users
- **Lambda Concurrency**: 1000 (default limit)
- **API Gateway**: 10,000 requests/second (default limit)

---

## 6. Reliability Design

### 6.1 High Availability

- **Multi-AZ Deployment**: Lambda functions in multiple availability zones
- **API Gateway**: Regional service with built-in redundancy
- **CloudFront**: Global edge locations for frontend

### 6.2 Error Handling

- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breaker**: Prevent cascading failures
- **Graceful Degradation**: Partial functionality if services unavailable
- **User-Friendly Errors**: Clear error messages without exposing internals

### 6.3 Monitoring and Alerting

- **CloudWatch Logs**: All operations logged
- **CloudWatch Metrics**: API latency, error rates, request counts
- **X-Ray Tracing**: Distributed tracing for debugging
- **Alarms**: Alert on error rate spikes, latency increases

---

## 7. Deployment Architecture

### 7.1 Infrastructure as Code

- **AWS SAM**: Serverless Application Model for Lambda/API Gateway
- **Terraform**: Alternative for complex infrastructure
- **GitHub Actions**: CI/CD pipeline

### 7.2 Environment Strategy

- **Development**: Isolated AWS account
- **Staging**: Production-like environment
- **Production**: Multi-region deployment

### 7.3 Deployment Process

```
1. Code commit to main branch
2. GitHub Actions triggered
3. Run tests (unit, integration)
4. Build Lambda package
5. Deploy to staging
6. Run smoke tests
7. Manual approval
8. Deploy to production
9. Post-deployment verification
```

---

## 8. Technology Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend Framework | Next.js | 14+ |
| Frontend Language | TypeScript | 5+ |
| UI Library | React | 18+ |
| Styling | Tailwind CSS | 3+ |
| Auth Library | MSAL.js | 3+ |
| Backend Framework | FastAPI | 0.104+ |
| Backend Language | Python | 3.12 |
| Runtime | AWS Lambda | Python 3.12 |
| API Gateway | AWS API Gateway | HTTP API |
| AWS SDK | boto3 | Latest |
| Infrastructure | AWS SAM | Latest |
| CI/CD | GitHub Actions | Latest |

---

## 9. Integration Points

### 9.1 Microsoft Entra ID Integration

- **OIDC Discovery**: `https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration`
- **JWKS Endpoint**: `https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys`
- **Token Endpoint**: `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token`
- **Required Claims**: `sub`, `email`, `groups` (for role mapping)

### 9.2 AWS Services Integration

- **AWS STS**: AssumeRole API for cross-account access
- **AWS Cognito**: User Pool management APIs
- **CloudWatch**: Logging and metrics
- **IAM**: Role trust relationships

---

## 10. Non-Functional Requirements Mapping

| NFR | Design Decision |
|-----|----------------|
| Performance (<2s p95) | Lambda optimization, credential caching, async I/O |
| Security (HTTPS, JWT) | API Gateway HTTPS, JWT validation middleware |
| Availability (99.9%) | Multi-AZ, auto-scaling, health checks |
| Scalability (100+ users) | Serverless architecture, auto-scaling |
| Auditability | CloudWatch Logs, structured logging |

---

**Document Control**

- **Version**: 1.0
- **Last Updated**: 2024
- **Next Review**: Quarterly or on major changes

