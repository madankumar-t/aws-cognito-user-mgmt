# .env File Format Guide
## Correct Format for Backend Configuration

---

## ✅ Correct .env File Format

Create `backend/.env` file with this format:

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

# Account Configuration (IMPORTANT!)
ALLOWED_ACCOUNTS=123456789012,987654321098
ACCOUNTS_CONFIG_SOURCE=env
ACCOUNTS_ENV_VAR=ALLOWED_ACCOUNTS
```

---

## 📝 Important Notes

### ALLOWED_ORIGINS Format

**✅ CORRECT:**
```bash
ALLOWED_ORIGINS=http://localhost:3000
```

**✅ CORRECT (multiple):**
```bash
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

**❌ WRONG:**
```bash
ALLOWED_ORIGINS=["http://localhost:3000"]  # No brackets
ALLOWED_ORIGINS='http://localhost:3000'    # No quotes needed
ALLOWED_ORIGINS= http://localhost:3000     # No leading space
```

### ALLOWED_ACCOUNTS Format

**✅ CORRECT:**
```bash
ALLOWED_ACCOUNTS=123456789012,987654321098
```

**❌ WRONG:**
```bash
ALLOWED_ACCOUNTS=123456789012, 987654321098  # No spaces after comma
ALLOWED_ACCOUNTS="123456789012,987654321098"  # No quotes
```

---

## 🔧 Quick Fix for Your Error

1. **Open `backend/.env` file**

2. **Check the `ALLOWED_ORIGINS` line**:
   - Should be: `ALLOWED_ORIGINS=http://localhost:3000`
   - Should NOT have brackets `[]`
   - Should NOT have quotes around the value
   - Should NOT have spaces

3. **If you have multiple origins**:
   ```bash
   ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
   ```
   (No spaces after comma)

4. **Save the file**

5. **Restart backend**:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

---

## 📋 Complete Example

```bash
# Copy this template and fill in your values

ENTRA_ID_TENANT_ID=your-tenant-id-here
ENTRA_ID_CLIENT_ID=your-client-id-here
ENTRA_ID_AUDIENCE=api://your-client-id-here
ACCOUNT_ROLE_NAME=CognitoManagementRole
DEFAULT_REGION=us-east-1
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000
ADMIN_GROUP_NAME=cognito-admin
DEVELOPER_GROUP_NAME=cognito-developer
ALLOWED_ACCOUNTS=123456789012,987654321098
ACCOUNTS_CONFIG_SOURCE=env
ACCOUNTS_ENV_VAR=ALLOWED_ACCOUNTS
```

---

## ✅ Verification

After fixing, the backend should start without errors:

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

**The code has been updated to handle comma-separated strings correctly!**

