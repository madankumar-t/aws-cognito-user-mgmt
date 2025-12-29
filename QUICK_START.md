# Quick Start Guide
## AWS Cognito User Management Application

**Fast deployment guide for experienced users**

---

## Prerequisites Checklist

- [ ] AWS CLI configured (`aws configure`)
- [ ] AWS SAM CLI installed (`sam --version`)
- [ ] Python 3.12 installed (latest stable)
- [ ] Node.js 18+ installed
- [ ] Microsoft Entra ID app registered
- [ ] IAM roles created in target accounts

---

## 1. Microsoft Entra ID Setup (5 minutes)

```bash
# 1. Register app in Azure Portal
# 2. Note: Tenant ID, Client ID
# 3. Create groups: cognito-admin, cognito-developer
# 4. Add users to groups
# 5. Configure redirect URI: http://localhost:3000
```

---

## 2. AWS IAM Setup (10 minutes)

```bash
# For each target account, create role:
aws iam create-role \
  --role-name CognitoManagementRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::<LAMBDA_ACCOUNT_ID>:root"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach Cognito policy (see BUILD_AND_DEPLOYMENT.md for full policy)
```

---

## 3. Backend Deployment (10 minutes)

```bash
cd backend

# 1. Configure environment
cp .env.example .env
# Edit .env with your values

# 2. Build
sam build

# 3. Deploy (first time - guided)
sam deploy --guided
# Enter: Tenant ID, Client ID, Audience, Allowed Origins

# 4. Note API URL from output
# Example: https://xxxxx.execute-api.us-east-1.amazonaws.com/prod
```

**Required Parameters:**
- `EntraIdTenantId`: Your Azure AD tenant ID
- `EntraIdClientId`: Your Azure AD client ID  
- `EntraIdAudience`: Usually `api://your-client-id`
- `AllowedOrigins`: `http://localhost:3000,https://your-domain.com`

---

## 4. Frontend Deployment (10 minutes)

```bash
cd frontend

# 1. Configure environment
cp .env.example .env.local
# Edit .env.local:
# NEXT_PUBLIC_API_URL=https://your-api-url-from-step-3
# NEXT_PUBLIC_ENTRA_ID_TENANT_ID=your-tenant-id
# NEXT_PUBLIC_ENTRA_ID_CLIENT_ID=your-client-id
# NEXT_PUBLIC_ENTRA_ID_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
# NEXT_PUBLIC_ENTRA_ID_REDIRECT_URI=http://localhost:3000

# 2. Install dependencies
npm install

# 3. Test locally
npm run dev
# Open http://localhost:3000

# 4. Build for production
npm run build

# 5. Deploy (Vercel example)
npm i -g vercel
vercel --prod
```

---

## 5. Verify Deployment (5 minutes)

```bash
# Backend health check
curl https://your-api-url/health
# Expected: {"status":"healthy","version":"1.0.0"}

# Frontend
# 1. Open your frontend URL
# 2. Click "Sign in with Microsoft"
# 3. Complete login
# 4. Verify dashboard loads
```

---

## 6. Configure Accounts

```bash
# Update Lambda environment variable
aws lambda update-function-configuration \
  --function-name your-function-name \
  --environment Variables="{ALLOWED_ACCOUNTS=123456789012,987654321098,...}"
```

---

## Common Commands

### Backend
```bash
# Build
sam build

# Deploy
sam deploy

# View logs
aws logs tail /aws/lambda/your-function-name --follow

# Update environment
sam deploy --parameter-overrides AllowedOrigins=...
```

### Frontend
```bash
# Development
npm run dev

# Build
npm run build

# Deploy (Vercel)
vercel --prod
```

---

## Troubleshooting

**401 Unauthorized:**
- Check JWT token validity
- Verify Entra ID configuration
- Check token expiration

**403 Forbidden:**
- Verify user is in `cognito-admin` or `cognito-developer` group
- Check role mapping

**STS AssumeRole fails:**
- Verify IAM role trust policy
- Check role ARN format
- Verify role exists

**CORS errors:**
- Check `ALLOWED_ORIGINS` includes frontend URL
- Verify exact URL match (including protocol)

---

## Full Documentation

For detailed instructions, see:
- **BUILD_AND_DEPLOYMENT.md** - Complete step-by-step guide
- **DEPLOYMENT.md** - Deployment reference
- **docs/** - Architecture and design documents

---

**Total Time:** ~40 minutes for complete setup

