# Fix: Pydantic Settings Error
## "error parsing value for field allowed_origins"

---

## 🚨 The Problem

You're getting this error because Pydantic Settings is trying to parse `ALLOWED_ORIGINS` from your `.env` file as JSON, but it's likely formatted as a comma-separated string.

---

## ✅ Solution

### Option 1: Format as JSON in .env (Quick Fix)

In your `backend/.env` file, format `ALLOWED_ORIGINS` as JSON:

```bash
# Format as JSON array
ALLOWED_ORIGINS=["http://localhost:3000"]
```

Or for multiple origins:

```bash
ALLOWED_ORIGINS=["http://localhost:3000","https://your-domain.com"]
```

### Option 2: Use Comma-Separated String (Recommended)

The code has been updated to handle comma-separated strings. In your `backend/.env` file:

```bash
# Simple comma-separated format (no brackets, no quotes around the whole thing)
ALLOWED_ORIGINS=http://localhost:3000
```

Or for multiple:

```bash
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

**No spaces after commas!**

---

## 📝 Correct .env Format

Your `backend/.env` file should look like this:

```bash
# Microsoft Entra ID
ENTRA_ID_TENANT_ID=your-tenant-id
ENTRA_ID_CLIENT_ID=your-client-id
ENTRA_ID_AUDIENCE=api://your-client-id

# AWS Accounts
ALLOWED_ACCOUNTS=123456789012,987654321098

# CORS - Use comma-separated format (no brackets)
ALLOWED_ORIGINS=http://localhost:3000

# Other settings
LOG_LEVEL=INFO
ACCOUNT_ROLE_NAME=CognitoManagementRole
```

---

## 🔧 If Error Persists

1. **Check your .env file format**:
   - No extra quotes around values
   - No brackets unless using JSON format
   - No trailing spaces

2. **Try removing ALLOWED_ORIGINS**:
   - The default is `http://localhost:3000`
   - You can omit it if that's all you need

3. **Check for hidden characters**:
   - Re-type the line if copied from somewhere
   - Ensure no special characters

---

## ✅ After Fixing

1. Save the `.env` file
2. Restart the backend server:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```
3. Should start without errors

---

**The code has been updated to handle both JSON and comma-separated formats!**

