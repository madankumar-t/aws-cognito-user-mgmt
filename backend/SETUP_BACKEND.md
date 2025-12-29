# Backend Setup Guide
## How to Start Backend and Configure AWS Accounts

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create .env File

Create `backend/.env` file with:

```bash
# Microsoft Entra ID
ENTRA_ID_TENANT_ID=your-tenant-id
ENTRA_ID_CLIENT_ID=your-client-id
ENTRA_ID_AUDIENCE=api://your-client-id

# AWS Accounts (IMPORTANT!)
ALLOWED_ACCOUNTS=123456789012,987654321098

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Start Server

```bash
uvicorn src.main:app --reload --port 8000
```

### 4. Verify

Open: http://localhost:8000/health

---

## Configure AWS Accounts

Edit `backend/.env` and set:

```bash
ALLOWED_ACCOUNTS=your-account-id-1,your-account-id-2
```

**No spaces**, comma-separated.

---

## Get Your AWS Account ID

```bash
aws sts get-caller-identity --query Account --output text
```

Or check AWS Console → Your username (top right) → Account ID

---

## Full .env Example

```bash
# Microsoft Entra ID Configuration
ENTRA_ID_TENANT_ID=12345678-1234-1234-1234-123456789abc
ENTRA_ID_CLIENT_ID=87654321-4321-4321-4321-cba987654321
ENTRA_ID_AUDIENCE=api://87654321-4321-4321-4321-cba987654321

# AWS Configuration
ACCOUNT_ROLE_NAME=CognitoManagementRole
DEFAULT_REGION=us-east-1

# Application Configuration
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000

# Role Mapping
ADMIN_GROUP_NAME=cognito-admin
DEVELOPER_GROUP_NAME=cognito-developer

# Account Configuration (IMPORTANT - Add your AWS account IDs here!)
ALLOWED_ACCOUNTS=123456789012,987654321098

# Account Configuration Source
ACCOUNTS_CONFIG_SOURCE=env
ACCOUNTS_ENV_VAR=ALLOWED_ACCOUNTS
```

---

## Troubleshooting

**Backend won't start?**
- Check Python version: `python3.12 --version`
- Check dependencies: `pip install -r requirements.txt`
- Check for port conflicts: Try port 8001

**No accounts showing?**
- Check `ALLOWED_ACCOUNTS` in `.env`
- Restart backend after changing `.env`
- Check backend logs for errors

**Connection refused?**
- Ensure backend is running
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Verify port 8000 is not blocked

---

**See NETWORK_ERROR_SOLUTION.md for detailed troubleshooting**

