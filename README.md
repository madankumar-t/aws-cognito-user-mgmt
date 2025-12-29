# aws-cognito-user-mgmt
# AWS Cognito User Management Application

Enterprise-grade, production-ready AWS Cognito User Management application with Microsoft Entra ID authentication, multi-account support, and role-based access control.

## Features

### Authentication & Authorization
- Microsoft Entra ID (Azure AD) OIDC/OAuth2 authentication
- JWT token validation in backend
- Role-based access control (Admin, Developer)
- RBAC enforced at both frontend and backend

### Multi-Account & Multi-Region
- Support for multiple AWS accounts
- AWS STS AssumeRole for cross-account access
- No long-lived credentials
- Account → Region → Cognito Pool selection flow

### User Management
**Admin Capabilities:**
- List users
- Create users
- Enable/disable users
- Set password
- Reset password
- Force password reset
- View user attributes and status

**Developer Capabilities:**
- List user pools
- List users
- View user details (read-only)

## Architecture

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Runtime**: AWS Lambda
- **API Gateway**: HTTP API
- **Authentication**: JWT validation with Microsoft Entra ID
- **Services**: STS, Cognito, Audit, Config

### Frontend
- **Framework**: Next.js 14+ (React)
- **Authentication**: MSAL (Microsoft Authentication Library)
- **State Management**: Zustand
- **Styling**: Tailwind CSS

## Project Structure

```
.
├── backend/              # FastAPI backend application
│   ├── src/
│   │   ├── main.py      # FastAPI app
│   │   ├── middleware/  # Auth, authorization, logging
│   │   ├── services/    # Business logic
│   │   ├── models/      # Pydantic models
│   │   └── routes/      # API routes
│   ├── lambda_handler.py
│   └── requirements.txt
├── frontend/            # Next.js frontend application
│   ├── src/
│   │   ├── app/         # Next.js app router
│   │   ├── components/  # React components
│   │   ├── lib/         # Utilities and API clients
│   │   └── store/        # State management
│   └── package.json
└── docs/                # Documentation
    ├── 01-BRD.md
    ├── 02-PRD.md
    ├── 03-HLD.md
    ├── 04-LLD.md
    └── ...
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
# Create .env file
# Add these required variables:
# ENTRA_ID_TENANT_ID=your-tenant-id
# ENTRA_ID_CLIENT_ID=your-client-id
# ENTRA_ID_AUDIENCE=api://your-client-id
# ALLOWED_ACCOUNTS=123456789012,987654321098  # Your AWS account IDs
# ALLOWED_ORIGINS=http://localhost:3000
```

4. Run locally:
```bash
uvicorn src.main:app --reload --port 8000
```

**Important**: The backend must be running for the frontend to work!

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. Run development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## Deployment

### Quick Start

For a fast deployment guide, see **[QUICK_START.md](QUICK_START.md)**

### Complete Guide

For detailed step-by-step instructions, see **[BUILD_AND_DEPLOYMENT.md](BUILD_AND_DEPLOYMENT.md)**

### Quick Commands

**Backend:**
```bash
cd backend
sam build
sam deploy --guided
```

**Frontend:**
```bash
cd frontend
npm run build
vercel --prod  # or your deployment method
```

## Configuration

### Microsoft Entra ID Setup

1. Register application in Azure AD
2. Configure redirect URIs
3. Create app roles/groups: `cognito-admin`, `cognito-developer`
4. Assign users to groups

### AWS IAM Setup

1. Create IAM role in Lambda account with STS AssumeRole permission
2. Create `CognitoManagementRole` in each target account
3. Configure trust relationship to allow Lambda account to assume role
4. Attach Cognito permissions policy

See `docs/09-IAM-Roles-and-Policies.md` for detailed IAM configuration.

## Documentation

Complete documentation is available in the `docs/` directory:

- **BRD**: Business Requirements Document
- **PRD**: Product Requirements Document
- **HLD**: High-Level Design
- **LLD**: Low-Level Design
- **Backend Architecture**: Backend structure and components
- **Frontend Architecture**: Frontend structure and components
- **Code Examples**: FastAPI and Lambda handler examples
- **IAM Policies**: IAM roles and policies
- **Security Considerations**: Security best practices
- **Future Enhancements**: Roadmap

## Security

- JWT token validation on every request
- No long-lived AWS credentials
- Temporary credentials via STS AssumeRole
- Role-based access control
- Input validation
- Structured logging
- Audit trails

See `docs/10-Security-Considerations.md` for detailed security information.

## Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## License

Proprietary - Internal Use Only

## Support

For issues and questions, contact the development team.

