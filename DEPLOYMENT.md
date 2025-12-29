# Deployment Guide
## AWS Cognito User Management Application

**Document Version:** 1.0  
**Date:** 2024

---

## 1. Prerequisites

### 1.1 Required Tools

- AWS CLI v2+
- AWS SAM CLI
- Python 3.12 (latest stable)
- Node.js 18+
- npm or yarn

### 1.2 AWS Account Setup

- AWS account with appropriate permissions
- IAM roles configured in target accounts
- Microsoft Entra ID app registration

---

## 2. Backend Deployment

### 2.1 Pre-Deployment Checklist

- [ ] Microsoft Entra ID app registered
- [ ] Environment variables configured
- [ ] IAM roles created in target accounts
- [ ] AWS credentials configured

### 2.2 Build and Deploy

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Build SAM application
sam build

# Deploy (guided mode for first time)
sam deploy --guided

# Or deploy with existing config
sam deploy
```

### 2.3 Environment Variables

Set the following parameters during deployment:

- `EntraIdTenantId`: Microsoft Entra ID tenant ID
- `EntraIdClientId`: Microsoft Entra ID client ID
- `EntraIdAudience`: Microsoft Entra ID audience
- `AccountRoleName`: IAM role name (default: CognitoManagementRole)
- `AllowedOrigins`: Comma-separated list of allowed CORS origins
- `LogLevel`: Log level (default: INFO)

### 2.4 Post-Deployment

1. Note the API Gateway URL from outputs
2. Update frontend environment variables with API URL
3. Test API endpoints
4. Verify CloudWatch Logs

---

## 3. Frontend Deployment

### 3.1 Build

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build
```

### 3.2 Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### 3.3 Deploy to AWS S3 + CloudFront

```bash
# Build
npm run build

# Upload to S3
aws s3 sync .next/static s3://your-bucket-name/static
aws s3 sync public s3://your-bucket-name/public

# Create CloudFront distribution
# Configure origin to S3 bucket
# Set default root object to index.html
```

### 3.4 Environment Variables

Set the following in your hosting platform:

- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_ENTRA_ID_TENANT_ID`: Microsoft Entra ID tenant ID
- `NEXT_PUBLIC_ENTRA_ID_CLIENT_ID`: Microsoft Entra ID client ID
- `NEXT_PUBLIC_ENTRA_ID_AUTHORITY`: Microsoft Entra ID authority URL
- `NEXT_PUBLIC_ENTRA_ID_REDIRECT_URI`: Redirect URI

---

## 4. IAM Role Setup

### 4.1 Lambda Execution Role

Created automatically by SAM. Verify it has:

- STS AssumeRole permission for target account roles
- CloudWatch Logs permissions
- CloudWatch Metrics permissions

### 4.2 Target Account Roles

In each target AWS account, create `CognitoManagementRole`:

1. Create IAM role with trust policy allowing Lambda account
2. Attach Cognito permissions policy
3. Note the role ARN

See `docs/09-IAM-Roles-and-Policies.md` for detailed policies.

---

## 5. Microsoft Entra ID Configuration

### 5.1 App Registration

1. Register application in Azure AD
2. Configure redirect URIs:
   - `http://localhost:3000` (development)
   - `https://your-domain.com` (production)
3. Create app roles or groups:
   - `cognito-admin`
   - `cognito-developer`
4. Assign users to groups

### 5.2 API Permissions

- Microsoft Graph: `User.Read`
- OpenID: `openid`, `profile`, `email`

---

## 6. Configuration Management

### 6.1 Account Configuration

Accounts can be configured via:

**Option 1: Environment Variables**
```bash
ALLOWED_ACCOUNTS=123456789012,987654321098
```

**Option 2: AWS Systems Manager Parameter Store**
```bash
aws ssm put-parameter \
  --name "/cognito-management/accounts" \
  --value '{"123456789012":{"name":"Production","regions":["us-east-1"]}}' \
  --type "String"
```

### 6.2 Update Configuration

After deployment, update account configuration:

1. Update environment variable or Parameter Store
2. Restart Lambda function (or wait for next invocation)

---

## 7. Testing Deployment

### 7.1 Health Check

```bash
curl https://your-api-url/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### 7.2 Authentication Test

1. Open frontend URL
2. Click "Sign in with Microsoft"
3. Complete authentication
4. Verify redirect to dashboard

### 7.3 API Test

```bash
# Get access token (from browser after login)
TOKEN="your-jwt-token"

# Test accounts endpoint
curl -H "Authorization: Bearer $TOKEN" \
  https://your-api-url/api/v1/accounts
```

---

## 8. Monitoring

### 8.1 CloudWatch Logs

- Log group: `/aws/lambda/CognitoManagementFunction`
- View logs: AWS Console → CloudWatch → Logs

### 8.2 CloudWatch Metrics

- Namespace: `CognitoManagement`
- Custom metrics: API calls, errors, latency

### 8.3 Alarms

Set up CloudWatch alarms for:
- Error rate > 1%
- Latency > 2 seconds (p95)
- Lambda function errors

---

## 9. Troubleshooting

### 9.1 Common Issues

**Issue**: 401 Unauthorized
- Check JWT token is valid
- Verify Microsoft Entra ID configuration
- Check token expiration

**Issue**: 403 Forbidden
- Verify user has required role
- Check role mapping configuration
- Verify groups in token

**Issue**: STS AssumeRole fails
- Check IAM role trust policy
- Verify role ARN is correct
- Check Lambda execution role permissions

**Issue**: Cognito operations fail
- Verify target account role has Cognito permissions
- Check User Pool ID is correct
- Verify region is correct

### 9.2 Debug Mode

Enable debug logging:

```bash
# Update Lambda environment variable
LOG_LEVEL=DEBUG

# Or via SAM
sam deploy --parameter-overrides LogLevel=DEBUG
```

---

## 10. Rollback

### 10.1 Backend Rollback

```bash
# List previous deployments
aws cloudformation list-stack-resources --stack-name cognito-management-api

# Rollback to previous version
sam deploy --parameter-overrides ... --no-execute-changeset
```

### 10.2 Frontend Rollback

- Vercel: Use deployment history
- S3/CloudFront: Upload previous build

---

## 11. Security Checklist

- [ ] HTTPS enforced everywhere
- [ ] CORS properly configured
- [ ] IAM roles follow least privilege
- [ ] No hardcoded credentials
- [ ] Environment variables encrypted
- [ ] CloudWatch Logs encrypted
- [ ] WAF rules configured (if applicable)
- [ ] Rate limiting enabled

---

## 12. Post-Deployment Tasks

1. Update documentation with production URLs
2. Configure monitoring and alerts
3. Set up backup procedures
4. Document runbooks
5. Train operations team
6. Schedule regular security reviews

---

**Document Control**

- **Version**: 1.0
- **Last Updated**: 2024

