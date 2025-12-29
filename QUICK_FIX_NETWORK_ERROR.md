# Quick Fix: Network Error
## Backend Connection Refused

---

## 🚨 The Problem

You're seeing "Network Error" because the **backend API server is not running**.

The frontend is trying to connect to `http://localhost:8000` but nothing is listening there.

---

## ✅ Quick Fix (3 Steps)

### Step 1: Start the Backend Server

Open a **new terminal window** and run:

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2: Verify Backend is Running

Open in browser: http://localhost:8000/health

Or in terminal:
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","version":"1.0.0"}`

### Step 3: Configure AWS Accounts

Edit `backend/.env` file and add:

```bash
ALLOWED_ACCOUNTS=123456789012,987654321098
```

Replace with your actual AWS account IDs (comma-separated).

**Then restart the backend** (Ctrl+C and start again).

---

## 🔍 Verify Everything Works

1. **Backend running**: http://localhost:8000/health ✅
2. **Frontend running**: http://localhost:3000 ✅
3. **Frontend `.env.local` has**: `NEXT_PUBLIC_API_URL=http://localhost:8000` ✅
4. **Backend `.env` has**: `ALLOWED_ACCOUNTS=your-account-ids` ✅

---

## 📋 Complete Setup

### Backend `.env` File Should Have:

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

### Frontend `.env.local` File Should Have:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENTRA_TENANT_ID=your-tenant-id
NEXT_PUBLIC_ENTRA_CLIENT_ID=your-client-id
```

---

## 🎯 After Fixing

1. Refresh the browser at http://localhost:3000/dashboard/accounts
2. You should see your AWS accounts listed
3. Click on an account to proceed

---

**That's it!** The network error should be resolved once the backend is running.

