# Backend Setup and Configuration
## How to Start Backend and Configure AWS Accounts

---

## 🚨 Issue: Network Error / Connection Refused

If you see "Network Error" or "ERR_CONNECTION_REFUSED", it means the **backend server is not running**.

---

## Step 1: Start the Backend Server

### Prerequisites

1. **Python 3.12** installed
2. **Backend dependencies** installed

### Start Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if using one)
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the server
uvicorn src.main:app --reload --port 8000
```

### Verify Backend is Running

Open a browser or use curl:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","version":"1.0.0"}
```

Or open in browser: http://localhost:8000/health

---

## Step 2: Configure AWS Accounts

The backend needs to know which AWS accounts you want to manage.

### Option 1: Environment Variable (Recommended for Development)

1. **Edit backend `.env` file**:

```bash
cd backend
nano .env  # or use your preferred editor
```

2. **Add/Update the `ALLOWED_ACCOUNTS` variable**:

```bash
ALLOWED_ACCOUNTS=123456789012,987654321098,111111111111
```

Replace with your actual AWS account IDs (comma-separated, no spaces).

3. **Restart the backend server** (if it's running):
   - Stop with `Ctrl+C`
   - Start again: `uvicorn src.main:app --reload --port 8000`

### Option 2: Set Environment Variable Directly

```bash
# Windows (PowerShell)
$env:ALLOWED_ACCOUNTS="123456789012,987654321098"

# Windows (CMD)
set ALLOWED_ACCOUNTS=123456789012,987654321098

# Linux/Mac
export ALLOWED_ACCOUNTS=123456789012,987654321098

# Then start server
uvicorn src.main:app --reload --port 8000
```

---

## Step 3: Configure AWS IAM Roles

For each AWS account you want to manage, you need to:

### 3.1 Create IAM Role in Target Account

In each AWS account where you want to manage Cognito pools:

1. **Go to IAM Console** → **Roles** → **Create role**

2. **Trust Policy**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::<LAMBDA_ACCOUNT_ID>:root"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```
   Replace `<LAMBDA_ACCOUNT_ID>` with the account ID where your Lambda function runs.

3. **Permissions Policy**:
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
           "cognito-idp:AdminResetUserPassword"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

4. **Role Name**: `CognitoManagementRole` (or match what's in your config)

5. **Note the Role ARN** for reference

### 3.2 For Local Development (Testing)

If you're testing locally (not deployed to Lambda), you'll need to:

1. **Configure AWS credentials** for local testing:
   ```bash
   aws configure
   ```

2. **Update the trust policy** to allow your local user/role to assume the role

---

## Step 4: Verify Configuration

### Test Backend API

```bash
# 1. Health check (no auth required)
curl http://localhost:8000/health

# 2. Get accounts (requires JWT token)
# First, get your JWT token from browser (after login)
# Then:
TOKEN="your-jwt-token-here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/accounts
```

### Test from Frontend

1. **Ensure backend is running**: http://localhost:8000/health
2. **Ensure frontend `.env.local` has**:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. **Restart frontend** if you just added the variable
4. **Refresh the browser** at http://localhost:3000/dashboard/accounts

---

## Complete Setup Checklist

### Backend Setup
- [ ] Python 3.12 installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with:
  - [ ] `ENTRA_ID_TENANT_ID`
  - [ ] `ENTRA_ID_CLIENT_ID`
  - [ ] `ENTRA_ID_AUDIENCE`
  - [ ] `ALLOWED_ACCOUNTS` (comma-separated account IDs)
- [ ] Backend server running (`uvicorn src.main:app --reload`)
- [ ] Health check works: http://localhost:8000/health

### AWS IAM Setup
- [ ] IAM role `CognitoManagementRole` created in each target account
- [ ] Trust policy allows Lambda account (or local account for testing)
- [ ] Permissions policy attached with Cognito permissions
- [ ] Role name matches configuration (default: `CognitoManagementRole`)

### Frontend Setup
- [ ] `.env.local` configured with:
  - [ ] `NEXT_PUBLIC_API_URL=http://localhost:8000`
  - [ ] `NEXT_PUBLIC_ENTRA_TENANT_ID`
  - [ ] `NEXT_PUBLIC_ENTRA_CLIENT_ID`
- [ ] Frontend server running (`npm run dev`)

---

## Troubleshooting

### Issue: "Cannot connect to backend API"

**Solution**:
1. Check if backend is running: `curl http://localhost:8000/health`
2. Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local`
3. Check backend logs for errors
4. Ensure no firewall blocking port 8000

### Issue: "Empty accounts list"

**Solution**:
1. Check `ALLOWED_ACCOUNTS` in backend `.env`
2. Verify format: comma-separated, no spaces
3. Restart backend after changing `.env`
4. Check backend logs for errors

### Issue: "401 Unauthorized" when calling API

**Solution**:
1. Verify JWT token is being sent (check browser Network tab)
2. Check backend JWT validation configuration
3. Verify `ENTRA_ID_TENANT_ID`, `ENTRA_ID_CLIENT_ID`, `ENTRA_ID_AUDIENCE` in backend `.env`

### Issue: "403 Forbidden" when calling API

**Solution**:
1. Verify user has required role (Admin or Developer)
2. Check groups/roles in token (use debug page: `/dashboard/debug`)
3. Verify role mapping in backend config

---

## Quick Start Commands

```bash
# Terminal 1: Start Backend
cd backend
uvicorn src.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev

# Terminal 3: Test Backend
curl http://localhost:8000/health
```

---

## Example Configuration

### Backend `.env`:
```bash
ENTRA_ID_TENANT_ID=12345678-1234-1234-1234-123456789abc
ENTRA_ID_CLIENT_ID=87654321-4321-4321-4321-cba987654321
ENTRA_ID_AUDIENCE=api://87654321-4321-4321-4321-cba987654321
ALLOWED_ACCOUNTS=123456789012,987654321098
ALLOWED_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

### Frontend `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENTRA_TENANT_ID=12345678-1234-1234-1234-123456789abc
NEXT_PUBLIC_ENTRA_CLIENT_ID=87654321-4321-4321-4321-cba987654321
```

---

**Last Updated**: 2024

