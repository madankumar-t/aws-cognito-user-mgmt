# AWS Cognito User Management - Backend

Enterprise-grade backend API for managing AWS Cognito users across multiple accounts and regions.

## Features

- Microsoft Entra ID (Azure AD) authentication via OIDC/OAuth2
- JWT token validation
- Role-based access control (Admin, Developer)
- Multi-account support via AWS STS AssumeRole
- Multi-region support
- Comprehensive user management operations
- Structured logging and audit trails

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run locally:
```bash
uvicorn src.main:app --reload --port 8000
```

## Deployment

Deploy using AWS SAM:

```bash
sam build
sam deploy --guided
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest
```

