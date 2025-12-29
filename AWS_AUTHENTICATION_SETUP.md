# AWS Authentication Setup Guide

## Overview

The backend uses **AWS STS AssumeRole** to access Cognito resources across multiple AWS accounts. This guide explains how to configure AWS authentication for both local development and production deployment.

---

## How It Works

1. **Backend receives request** → Validates JWT token from Entra ID
2. **Backend assumes IAM role** → Uses STS AssumeRole to get temporary credentials for target AWS account
3. **Backend accesses Cognito** → Uses temporary credentials to manage Cognito resources

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │   Backend    │ ──────> │  AWS STS    │
│  (Browser)  │  JWT    │  (FastAPI)   │ Assume  │  (Assume    │
│             │  Token  │              │  Role   │   Role)     │
└─────────────┘         └──────────────┘         └─────────────┘
                                                         │
                                                         v
                                                ┌─────────────┐
                                                │ AWS Cognito │
                                                │  (Target    │
                                                │   Account)  │
                                                └─────────────┘
```

---

## Step 1: Configure AWS Credentials (Local Development)

For local development, the backend needs AWS credentials to call STS AssumeRole.

### Option A: AWS CLI Configuration (Recommended)

```bash
# Install AWS CLI if not already installed
# https://aws.amazon.com/cli/

# Configure credentials
aws configure

# Enter:
# - AWS Access Key ID: Your access key
# - AWS Secret Access Key: Your secret key
# - Default region: us-east-1 (or your preferred region)
# - Default output format: json
```

This creates `~/.aws/credentials` and `~/.aws/config` files.

### Option B: Environment Variables

```bash
# Windows PowerShell
$env:AWS_ACCESS_KEY_ID="your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret-access-key"
$env:AWS_DEFAULT_REGION="us-east-1"

# Linux/Mac
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Option C: IAM User with AssumeRole Permission

The IAM user/role used for local development needs permission to assume roles in target accounts:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::*:role/CognitoManagementRole"
    }
  ]
}
```

---

## Step 2: Create IAM Role in Target AWS Accounts

For each AWS account where you want to manage Cognito pools, create an IAM role that the backend can assume.

### 2.1 Create the Role

1. **Go to AWS Console** → **IAM** → **Roles** → **Create role**

2. **Select "AWS account"** as trusted entity type

3. **Configure Trust Policy**:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::<YOUR_ACCOUNT_ID>:root"
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
   ```

   **Replace `<YOUR_ACCOUNT_ID>`** with:
   - **For local dev**: Your AWS account ID where your credentials are from
   - **For production**: The AWS account ID where your Lambda function runs

4. **Add Permissions Policy**:

   ```json
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
           "cognito-idp:AdminResetUserPassword",
           "cognito-idp:AdminInitiateAuth",
           "cognito-idp:AdminRespondToAuthChallenge"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

5. **Role Name**: `CognitoManagementRole` (or match `ACCOUNT_ROLE_NAME` in your `.env`)

6. **Create the role**

### 2.2 Note the Role ARN

After creating the role, note the **Role ARN**:
```
arn:aws:iam::<TARGET_ACCOUNT_ID>:role/CognitoManagementRole
```

---

## Step 3: Configure Backend Environment

Update your `backend/.env` file:

```bash
# AWS Account Configuration
ALLOWED_ACCOUNTS=123456789012,987654321098

# AWS Role Name (must match the role you created)
ACCOUNT_ROLE_NAME=CognitoManagementRole

# Default AWS Region
DEFAULT_REGION=us-east-1
```

**Format for `ALLOWED_ACCOUNTS`**:
- Simple: `123456789012,987654321098`
- With names: `123456789012:Production Account,987654321098:Development Account`

---

## Step 4: Verify AWS Authentication

### 4.1 Test AWS Credentials

```bash
# Test that your AWS credentials work
aws sts get-caller-identity

# Should return:
# {
#     "UserId": "...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```

### 4.2 Test AssumeRole (Manual)

```bash
# Test assuming the role in a target account
aws sts assume-role \
  --role-arn "arn:aws:iam::<TARGET_ACCOUNT_ID>:role/CognitoManagementRole" \
  --role-session-name "test-session"

# Should return temporary credentials
```

### 4.3 Test Backend API

1. **Start the backend**:
   ```bash
   cd backend
   uvicorn src.main:app --reload --port 8000
   ```

2. **Test health endpoint** (no auth required):
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test accounts endpoint** (requires JWT token):
   - Login via frontend first to get JWT token
   - Or use browser DevTools → Network tab → Copy Authorization header
   ```bash
   curl -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
        http://localhost:8000/api/v1/accounts
   ```

---

## Step 5: Troubleshooting

### Error: "AccessDenied" when assuming role

**Cause**: The trust policy doesn't allow your AWS account/user to assume the role.

**Fix**:
1. Check the trust policy in the target account's IAM role
2. Ensure the Principal ARN matches your AWS account ID
3. For local dev, you might need to allow your specific IAM user:
   ```json
   {
     "Principal": {
       "AWS": [
         "arn:aws:iam::<YOUR_ACCOUNT_ID>:root",
         "arn:aws:iam::<YOUR_ACCOUNT_ID>:user/<YOUR_USERNAME>"
       ]
     }
   }
   ```

### Error: "No accounts configured"

**Cause**: `ALLOWED_ACCOUNTS` environment variable is not set or empty.

**Fix**:
1. Check `backend/.env` file
2. Ensure `ALLOWED_ACCOUNTS` is set with comma-separated account IDs
3. Restart the backend server

### Error: "Failed to assume role: InvalidClientTokenId"

**Cause**: AWS credentials are not configured or invalid.

**Fix**:
1. Run `aws configure` to set up credentials
2. Test with `aws sts get-caller-identity`
3. Ensure credentials have `sts:AssumeRole` permission

### Error: "Missing or invalid authorization header" (401)

**Cause**: Frontend is not sending JWT token, or token is invalid.

**Fix**:
1. Ensure you're logged in via Entra ID
2. Check browser DevTools → Network tab → Request Headers
3. Verify `Authorization: Bearer <token>` is present
4. Check frontend API client is attaching tokens correctly

### Error: "Network Error" in Frontend

**Cause**: Backend server is not running or not accessible.

**Fix**:
1. Ensure backend is running: `uvicorn src.main:app --reload --port 8000`
2. Check `NEXT_PUBLIC_API_URL` in frontend `.env` matches backend URL
3. Check CORS settings in `backend/.env` (`ALLOWED_ORIGINS`)

---

## Step 6: Production Deployment

For production (AWS Lambda), the setup is similar but:

1. **Lambda Execution Role**: The Lambda function's execution role needs `sts:AssumeRole` permission
2. **Trust Policy**: Target account roles should trust the Lambda's account ID
3. **Environment Variables**: Set `ALLOWED_ACCOUNTS` and `ACCOUNT_ROLE_NAME` in Lambda configuration

### Lambda Execution Role Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::*:role/CognitoManagementRole"
    }
  ]
}
```

---

## Summary Checklist

- [ ] AWS credentials configured locally (`aws configure` or environment variables)
- [ ] IAM role created in each target AWS account with name `CognitoManagementRole`
- [ ] Trust policy allows your AWS account to assume the role
- [ ] Permissions policy grants Cognito management actions
- [ ] `ALLOWED_ACCOUNTS` set in `backend/.env` with target account IDs
- [ ] `ACCOUNT_ROLE_NAME` matches the role name in target accounts
- [ ] Backend server starts without errors
- [ ] Can assume role manually: `aws sts assume-role --role-arn ...`
- [ ] Frontend can authenticate and receive JWT token
- [ ] API calls from frontend include `Authorization: Bearer <token>` header

---

## Additional Resources

- [AWS STS AssumeRole Documentation](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html)
- [IAM Roles for Cross-Account Access](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_aws-accounts.html)
- [AWS Cognito IAM Permissions](https://docs.aws.amazon.com/cognito/latest/developerguide/iam-roles.html)

