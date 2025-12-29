# Build and Deployment Instructions
## AWS Cognito User Management Application

**Complete step-by-step guide for building and deploying the application**

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Pre-Deployment Setup](#2-pre-deployment-setup)
3. [Backend Build and Deployment](#3-backend-build-and-deployment)
4. [Frontend Build and Deployment](#4-frontend-build-and-deployment)
5. [Post-Deployment Configuration](#5-post-deployment-configuration)
6. [Verification and Testing](#6-verification-and-testing)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Prerequisites

### 1.1 Required Software

Install the following tools on your local machine:

```bash
# AWS CLI (v2+)
# Download from: https://aws.amazon.com/cli/
aws --version

# AWS SAM CLI
# Install via: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
sam --version

# Python 3.12 (latest stable version)
python3 --version  # Should be 3.12.x or higher

# Node.js 18+ and npm
node --version     # Should be 18.x or higher
npm --version

# Git
git --version
```

### 1.2 AWS Account Setup

- AWS account with appropriate permissions
- AWS CLI configured with credentials:
  ```bash
  aws configure
  # Enter: Access Key ID, Secret Access Key, Region, Output format
  ```

### 1.3 Microsoft Entra ID Setup

- Access to Microsoft Entra ID (Azure AD) tenant
- Permissions to register applications

---

## 2. Pre-Deployment Setup

### 2.1 Microsoft Entra ID App Registration

#### Step 1: Register Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Fill in:
   - **Name**: `AWS Cognito Management App`
   - **Supported account types**: Your organization only
   - **Redirect URI**: 
     - Type: `Single-page application (SPA)`
     - URI: `http://localhost:3000` (for development)
5. Click **Register**
6. Note the following values:
   - **Application (client) ID**
   - **Directory (tenant) ID**

#### Step 2: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph** → **Delegated permissions**
4. Add:
   - `User.Read`
   - `openid`
   - `profile`
   - `email`
5. Click **Add permissions**
6. Click **Grant admin consent** (if you have admin rights)

#### Step 3: Create Groups for Role Mapping

1. Go to **Azure Active Directory** → **Groups**
2. Create two groups:
   - **Group 1**:
     - Name: `cognito-admin`
     - Type: Security
   - **Group 2**:
     - Name: `cognito-developer`
     - Type: Security
3. Add users to appropriate groups

#### Step 4: Configure App Roles (Alternative to Groups)

If using app roles instead of groups:

1. In app registration, go to **App roles**
2. Click **Create app role**
3. Create role:
   - Display name: `Cognito Admin`
   - Allowed member types: Users/Groups
   - Value: `cognito-admin`
   - Description: `Full access to Cognito user management`
4. Repeat for Developer role:
   - Value: `cognito-developer`
   - Description: `Read-only access to Cognito user management`
5. Assign users to roles

#### Step 5: Configure Redirect URIs for Production

1. In app registration, go to **Authentication**
2. Under **Single-page application**, add:
   - `https://your-domain.com` (production URL)
3. Save changes

### 2.2 AWS IAM Role Setup

#### Step 1: Create Lambda Execution Role (Auto-created by SAM)

The Lambda execution role will be created automatically during SAM deployment. Verify it has:
- STS AssumeRole permission
- CloudWatch Logs permissions
- CloudWatch Metrics permissions

#### Step 2: Create Cross-Account Role in Target Accounts

For each AWS account where you want to manage Cognito pools:

1. **Get Lambda Account ID**:
   ```bash
   aws sts get-caller-identity --query Account --output text
   ```
   Note this account ID.

2. **Create IAM Role in Target Account**:
   ```bash
   # In target account, create role with this trust policy
   cat > trust-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::<LAMBDA_ACCOUNT_ID>:root"
         },
         "Action": "sts:AssumeRole",
         "Condition": {
           "StringEquals": {
             "sts:ExternalId": "optional-external-id"
           }
         }
       }
     ]
   }
   EOF
   
   # Create role
   aws iam create-role \
     --role-name CognitoManagementRole \
     --assume-role-policy-document file://trust-policy.json
   ```

3. **Attach Cognito Permissions Policy**:
   ```bash
   cat > cognito-policy.json <<EOF
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "cognito-idp:ListUserPools",
           "cognito-idp:DescribeUserPool",
           "cognito-idp:ListUsers",
           "cognito-idp:AdminGetUser",
           "cognito-idp:AdminCreateUser",
           "cognito-idp:AdminUpdateUserAttributes",
           "cognito-idp:AdminDeleteUser",
           "cognito-idp:AdminEnableUser",
           "cognito-idp:AdminDisableUser",
           "cognito-idp:AdminSetUserPassword",
           "cognito-idp:AdminResetUserPassword"
         ],
         "Resource": "*"
       }
     ]
   }
   EOF
   
   aws iam put-role-policy \
     --role-name CognitoManagementRole \
     --policy-name CognitoManagementPolicy \
     --policy-document file://cognito-policy.json
   ```

4. **Note the Role ARN** for each account

---

## 3. Backend Build and Deployment

### 3.1 Local Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your values
nano .env  # or use your preferred editor
```

**Required `.env` values:**
```bash
# Microsoft Entra ID Configuration
ENTRA_ID_TENANT_ID=your-tenant-id-here
ENTRA_ID_CLIENT_ID=your-client-id-here
ENTRA_ID_AUDIENCE=api://your-client-id-here
JWKS_URL=https://login.microsoftonline.com/your-tenant-id/discovery/v2.0/keys

# AWS Configuration
ACCOUNT_ROLE_NAME=CognitoManagementRole
DEFAULT_REGION=us-east-1

# Application Configuration
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com

# Role Mapping
ADMIN_GROUP_NAME=cognito-admin
DEVELOPER_GROUP_NAME=cognito-developer

# Account Configuration
ACCOUNTS_CONFIG_SOURCE=env
ALLOWED_ACCOUNTS=123456789012,987654321098
```

### 3.3 Test Locally (Optional)

```bash
# Run FastAPI locally
uvicorn src.main:app --reload --port 8000

# In another terminal, test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### 3.4 Build with SAM

```bash
# Ensure you're in backend directory
cd backend

# Build the application
sam build

# This will:
# - Install dependencies
# - Package the Lambda function
# - Create deployment artifacts in .aws-sam/build/
```

### 3.5 Deploy with SAM

#### First-Time Deployment (Guided)

```bash
sam deploy --guided
```

**You'll be prompted for:**
- Stack Name: `cognito-management-api` (or your choice)
- AWS Region: `us-east-1` (or your preferred region)
- Parameter EntraIdTenantId: Your Microsoft Entra ID tenant ID
- Parameter EntraIdClientId: Your Microsoft Entra ID client ID
- Parameter EntraIdAudience: Your Microsoft Entra ID audience (usually `api://client-id`)
- Parameter AccountRoleName: `CognitoManagementRole` (default)
- Parameter AllowedOrigins: `http://localhost:3000,https://your-domain.com`
- Parameter LogLevel: `INFO` (default)
- Confirm changes before deploy: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Disable rollback: `N`
- Save arguments to configuration file: `Y`

#### Subsequent Deployments

```bash
# Deploy using saved configuration
sam deploy

# Or deploy with parameter overrides
sam deploy --parameter-overrides \
  EntraIdTenantId=your-tenant-id \
  EntraIdClientId=your-client-id \
  EntraIdAudience=api://your-client-id \
  AllowedOrigins=http://localhost:3000,https://your-domain.com
```

### 3.6 Capture Deployment Outputs

After deployment, note the following from the output:

```bash
# API Gateway URL
ApiUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod

# Lambda Function Name
FunctionName = cognito-management-api-CognitoManagementFunction-xxxxx

# Lambda Function ARN
FunctionArn = arn:aws:lambda:us-east-1:xxxxxxxxxx:function:xxxxx
```

**Save the API URL** - you'll need it for frontend configuration.

### 3.7 Verify Backend Deployment

```bash
# Test health endpoint
curl https://your-api-url.execute-api.us-east-1.amazonaws.com/prod/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}

# Test API documentation
# Open in browser:
# https://your-api-url.execute-api.us-east-1.amazonaws.com/prod/docs
```

---

## 4. Frontend Build and Deployment

### 4.1 Local Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 4.2 Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local file
nano .env.local  # or use your preferred editor
```

**Required `.env.local` values:**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://your-api-url.execute-api.us-east-1.amazonaws.com/prod

# Microsoft Entra ID Configuration
NEXT_PUBLIC_ENTRA_ID_TENANT_ID=your-tenant-id-here
NEXT_PUBLIC_ENTRA_ID_CLIENT_ID=your-client-id-here
NEXT_PUBLIC_ENTRA_ID_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
NEXT_PUBLIC_ENTRA_ID_REDIRECT_URI=http://localhost:3000
```

### 4.3 Test Locally

```bash
# Run development server
npm run dev

# Open browser to http://localhost:3000
# You should see the login page
```

### 4.4 Build for Production

```bash
# Build the application
npm run build

# This creates optimized production build in .next/ directory
```

### 4.5 Deploy Frontend

#### Option A: Deploy to Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy (first time - interactive)
vercel

# Follow prompts:
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name: aws-cognito-management
# - Directory: ./
# - Override settings? N

# Deploy to production
vercel --prod

# Set environment variables in Vercel dashboard:
# - Go to project settings → Environment Variables
# - Add all NEXT_PUBLIC_* variables
```

#### Option B: Deploy to AWS Amplify (Recommended for AWS)

**AWS Amplify is the recommended AWS deployment option** as it properly handles Next.js applications with client-side features.

**Step 1: Connect Repository**

1. Go to AWS Amplify Console
2. Click "New app" → "Host web app"
3. Connect your Git repository (GitHub, GitLab, Bitbucket)
4. Select branch: `main` or `master`

**Step 2: Configure Build Settings**

Amplify auto-detects Next.js. Verify build settings:
- Build command: `npm run build`
- Output directory: `.next` (auto-detected)

**Step 3: Configure Environment Variables**

1. Go to App Settings → Environment Variables
2. Add all `NEXT_PUBLIC_*` variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_ENTRA_ID_TENANT_ID`
   - `NEXT_PUBLIC_ENTRA_ID_CLIENT_ID`
   - `NEXT_PUBLIC_ENTRA_ID_AUTHORITY`
   - `NEXT_PUBLIC_ENTRA_ID_REDIRECT_URI`

**Step 4: Deploy**

1. Click "Save and deploy"
2. Amplify will build and deploy automatically
3. Note the deployment URL

**Note:** S3 + CloudFront static hosting is **NOT recommended** for this application as it requires client-side JavaScript, authentication, and dynamic features that don't work with static export.

#### Option C: Deploy to Other Platforms

**Netlify:**
```bash
npm install -g netlify-cli
netlify deploy --prod
```

**AWS Amplify:**
- Connect GitHub repository
- Configure build settings
- Add environment variables in Amplify console

### 4.6 Update Redirect URI

After deployment, update Microsoft Entra ID redirect URI:

1. Go to Azure Portal → App registrations → Your app
2. Go to **Authentication**
3. Add production redirect URI:
   - `https://your-domain.com` (or your CloudFront/Vercel URL)
4. Save

---

## 5. Post-Deployment Configuration

### 5.1 Update Frontend Environment Variables

If deploying to a platform that requires environment variables:

**Vercel:**
- Go to Project Settings → Environment Variables
- Add all `NEXT_PUBLIC_*` variables
- Redeploy

**AWS Amplify:**
- Go to App Settings → Environment Variables
- Add all `NEXT_PUBLIC_*` variables
- Redeploy

### 5.2 Configure Account List

Update the account configuration in Lambda environment:

**Option 1: Update via AWS Console**
1. Go to Lambda → Your function → Configuration → Environment variables
2. Edit `ALLOWED_ACCOUNTS` variable
3. Add/remove account IDs (comma-separated)

**Option 2: Update via SAM**
```bash
sam deploy --parameter-overrides \
  AllowedAccounts=123456789012,987654321098,111111111111
```

**Option 3: Use Parameter Store**
```bash
aws ssm put-parameter \
  --name "/cognito-management/accounts" \
  --value '{"123456789012":{"name":"Production","regions":["us-east-1"]},"987654321098":{"name":"Development","regions":["us-east-1","us-west-2"]}}' \
  --type "String" \
  --overwrite
```

Then update Lambda environment:
```bash
# Set accounts_config_source to "ssm"
aws lambda update-function-configuration \
  --function-name your-function-name \
  --environment Variables="{ACCOUNTS_CONFIG_SOURCE=ssm,...}"
```

### 5.3 Configure CORS (if needed)

If you need to add additional origins:

```bash
# Update via SAM
sam deploy --parameter-overrides \
  AllowedOrigins=http://localhost:3000,https://your-domain.com,https://another-domain.com
```

---

## 6. Verification and Testing

### 6.1 Backend Verification

```bash
# 1. Health Check
curl https://your-api-url/health
# Expected: {"status":"healthy","version":"1.0.0"}

# 2. Check API Documentation
# Open: https://your-api-url/docs

# 3. Test Authentication (requires valid JWT token)
# Get token from browser after login, then:
TOKEN="your-jwt-token-here"
curl -H "Authorization: Bearer $TOKEN" \
  https://your-api-url/api/v1/auth/me
# Expected: User information with roles
```

### 6.2 Frontend Verification

1. **Open Application URL**
   - Development: `http://localhost:3000`
   - Production: `https://your-domain.com`

2. **Test Authentication Flow**
   - Click "Sign in with Microsoft"
   - Complete Microsoft login
   - Verify redirect to dashboard
   - Check user info in header

3. **Test Account Selection**
   - Should see list of configured accounts
   - Select an account
   - Verify navigation to region selection

4. **Test Region Selection**
   - Select a region
   - Verify navigation to pool selection

5. **Test Pool Selection**
   - Should see Cognito User Pools
   - Select a pool
   - Verify navigation to user management

6. **Test User Management**
   - **As Admin**: Should see all actions (Create, Enable/Disable, etc.)
   - **As Developer**: Should see read-only view
   - Test listing users
   - Test viewing user details

### 6.3 End-to-End Testing

**Test Admin Workflow:**
1. Login as user in `cognito-admin` group
2. Select account → region → pool
3. Create a test user
4. Enable/disable the user
5. Set password for the user
6. Verify operations in CloudWatch Logs

**Test Developer Workflow:**
1. Login as user in `cognito-developer` group
2. Select account → region → pool
3. Verify can list users
4. Verify can view user details
5. Verify cannot create/edit users (UI should hide buttons)

### 6.4 CloudWatch Verification

```bash
# Check Lambda logs
aws logs tail /aws/lambda/your-function-name --follow

# Check for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/your-function-name \
  --filter-pattern "ERROR"
```

---

## 7. Troubleshooting

### 7.1 Backend Issues

**Issue: SAM build fails**
```bash
# Check Python version
python3 --version  # Should be 3.12 or higher

# Clear build cache
rm -rf .aws-sam/
sam build --use-container  # Use Docker container
```

**Issue: Deployment fails - IAM permissions**
```bash
# Ensure your AWS credentials have:
# - CloudFormation permissions
# - Lambda permissions
# - IAM role creation permissions
# - API Gateway permissions

# Check with:
aws sts get-caller-identity
```

**Issue: 401 Unauthorized errors**
- Verify JWT token is valid
- Check Microsoft Entra ID configuration
- Verify `ENTRA_ID_TENANT_ID`, `ENTRA_ID_CLIENT_ID`, `ENTRA_ID_AUDIENCE`
- Check token expiration
- Verify JWKS URL is accessible

**Issue: 403 Forbidden errors**
- Verify user is in correct Entra ID group
- Check group names match configuration (`cognito-admin`, `cognito-developer`)
- Verify role mapping in backend config

**Issue: STS AssumeRole fails**
- Check IAM role trust policy in target account
- Verify Lambda account ID is correct
- Check role ARN format
- Verify role exists in target account

**Issue: Cognito operations fail**
- Verify target account role has Cognito permissions
- Check User Pool ID is correct
- Verify region matches User Pool region
- Check CloudWatch Logs for detailed error

### 7.2 Frontend Issues

**Issue: Build fails**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+

# Clear Next.js cache
rm -rf .next
npm run build
```

**Issue: Authentication doesn't work**
- Verify environment variables are set correctly
- Check `NEXT_PUBLIC_ENTRA_ID_*` variables
- Verify redirect URI matches Azure AD configuration
- Check browser console for errors
- Verify API URL is correct

**Issue: API calls fail with 401**
- Check if token is being sent in Authorization header
- Verify token is valid (not expired)
- Check API URL is correct
- Verify CORS is configured correctly

**Issue: CORS errors**
- Verify `ALLOWED_ORIGINS` in backend includes frontend URL
- Check API Gateway CORS configuration
- Verify frontend URL matches exactly (including protocol)

### 7.3 Common Configuration Issues

**Issue: Accounts not showing**
- Verify `ALLOWED_ACCOUNTS` environment variable is set
- Check account IDs are comma-separated
- Verify no extra spaces
- Check Lambda environment variables

**Issue: Pools not listing**
- Verify IAM role in target account has `cognito-idp:ListUserPools` permission
- Check region is correct
- Verify account ID is correct
- Check CloudWatch Logs for errors

### 7.4 Debug Mode

**Enable Debug Logging:**

Backend:
```bash
# Update Lambda environment variable
aws lambda update-function-configuration \
  --function-name your-function-name \
  --environment Variables="{LOG_LEVEL=DEBUG,...}"

# Or via SAM
sam deploy --parameter-overrides LogLevel=DEBUG
```

Frontend:
```bash
# Add to .env.local
NEXT_PUBLIC_DEBUG=true

# Check browser console for detailed logs
```

### 7.5 Getting Help

1. **Check Logs:**
   - CloudWatch Logs for backend
   - Browser console for frontend
   - Network tab for API calls

2. **Verify Configuration:**
   - Environment variables
   - IAM roles and policies
   - Microsoft Entra ID settings

3. **Test Components:**
   - Test backend endpoints directly
   - Test authentication separately
   - Test API calls with curl/Postman

---

## 8. Maintenance

### 8.1 Updating the Application

**Backend:**
```bash
cd backend
# Make code changes
sam build
sam deploy
```

**Frontend:**
```bash
cd frontend
# Make code changes
npm run build
# Redeploy to your platform
```

### 8.2 Monitoring

- Set up CloudWatch alarms for:
  - Lambda errors
  - API Gateway 4xx/5xx errors
  - High latency
- Monitor CloudWatch Logs regularly
- Review audit logs for security

### 8.3 Security Updates

- Keep dependencies updated:
  ```bash
  # Backend
  pip list --outdated
  pip install --upgrade package-name
  
  # Frontend
  npm outdated
  npm update
  ```
- Review and rotate credentials regularly
- Monitor for security advisories

---

## Quick Reference

### Backend Deployment
```bash
cd backend
sam build
sam deploy --parameter-overrides \
  EntraIdTenantId=xxx \
  EntraIdClientId=xxx \
  EntraIdAudience=api://xxx \
  AllowedOrigins=http://localhost:3000,https://your-domain.com
```

### Frontend Deployment
```bash
cd frontend
npm run build
vercel --prod  # or your deployment method
```

### Health Check
```bash
curl https://your-api-url/health
```

---

**Document Version:** 1.0  
**Last Updated:** 2024

