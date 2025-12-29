# Network Error Solution
## Fix "ERR_CONNECTION_REFUSED" Error

---

## 🔍 The Problem

You're seeing "Network Error" because:

1. **Backend server is not running** at `http://localhost:8000`
2. **Frontend cannot connect** to the backend API
3. The API call to `/api/v1/accounts` is failing

---

## ✅ Solution: Start the Backend

### Step 1: Open a New Terminal

Keep your frontend running, open a **new terminal window**.

### Step 2: Navigate to Backend Directory

```bash
cd backend
```

### Step 3: Install Dependencies (First Time Only)

```bash
# Create virtual environment (if not exists)
python3.12 -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create or edit `backend/.env` file:

```bash
# Copy example
cp .env.example .env

# Edit .env file
nano .env  # or use your editor
```

**Required values in `.env`**:

```bash
# Microsoft Entra ID
ENTRA_ID_TENANT_ID=your-tenant-id
ENTRA_ID_CLIENT_ID=your-client-id
ENTRA_ID_AUDIENCE=api://your-client-id

# AWS Accounts (IMPORTANT - Add your account IDs here!)
ALLOWED_ACCOUNTS=123456789012,987654321098

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

**Replace `123456789012,987654321098` with your actual AWS account IDs.**

### Step 5: Start the Backend Server

```bash
uvicorn src.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Step 6: Verify Backend is Running

Open in browser: **http://localhost:8000/health**

Should show: `{"status":"healthy","version":"1.0.0"}`

### Step 7: Refresh Frontend

Go back to your browser at **http://localhost:3000/dashboard/accounts** and refresh.

The network error should be gone, and you should see your AWS accounts listed!

---

## 📋 How to Get AWS Account IDs

### Option 1: AWS Console

1. Go to [AWS Console](https://console.aws.amazon.com)
2. Click on your username (top right)
3. Your **Account ID** is displayed there

### Option 2: AWS CLI

```bash
aws sts get-caller-identity --query Account --output text
```

### Option 3: From Existing Resources

- Check any existing AWS resource ARN
- Format: `arn:aws:service:region:ACCOUNT_ID:resource`
- The account ID is the number after the region

---

## 🔧 Configure Multiple Accounts

In `backend/.env`, add multiple account IDs (comma-separated):

```bash
ALLOWED_ACCOUNTS=123456789012,987654321098,111111111111
```

**No spaces** between account IDs!

---

## 🎯 Expected Result

After starting the backend:

1. ✅ Backend running at http://localhost:8000
2. ✅ Health check works: http://localhost:8000/health
3. ✅ Frontend can connect to backend
4. ✅ Accounts page shows your AWS accounts
5. ✅ You can select an account and proceed

---

## 🚨 Still Having Issues?

### Check 1: Backend is Running

```bash
# Test in terminal
curl http://localhost:8000/health

# Should return JSON, not connection error
```

### Check 2: Frontend Environment Variable

Verify `frontend/.env.local` has:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Check 3: Port Conflicts

If port 8000 is in use:

```bash
# Use different port
uvicorn src.main:app --reload --port 8001

# Then update frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Check 4: Firewall

Ensure your firewall allows connections to `localhost:8000`

---

## 📝 Quick Reference

**Backend Start Command**:
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Backend Health Check**:
```bash
curl http://localhost:8000/health
```

**Backend Configuration**:
- File: `backend/.env`
- Key variable: `ALLOWED_ACCOUNTS=account-id-1,account-id-2`

---

**The network error will be resolved once the backend is running!**

