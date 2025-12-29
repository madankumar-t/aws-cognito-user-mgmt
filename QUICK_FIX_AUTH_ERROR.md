# Quick Fix: Authentication and Network Errors

## Issue 1: "Missing or invalid authorization header" (401)

**Symptom**: Backend logs show `HTTPException: 401: Missing or invalid authorization header`

**Root Cause**: Frontend is not sending JWT token in API requests.

### Fix Steps:

1. **Verify you're logged in**:
   - Check browser DevTools → Application → Session Storage
   - Look for MSAL keys (should have `msal.account.keys` or similar)

2. **Check API client is attaching tokens**:
   - Open browser DevTools → Network tab
   - Make a request to `/api/v1/accounts`
   - Check Request Headers → Should have `Authorization: Bearer <token>`
   - If missing, the API client interceptor might not be working

3. **Verify MSAL configuration**:
   - Check `frontend/.env.local` has:
     ```
     NEXT_PUBLIC_ENTRA_CLIENT_ID=your-client-id
     NEXT_PUBLIC_ENTRA_TENANT_ID=your-tenant-id
     ```
   - Restart frontend dev server after changing `.env` files

4. **Clear browser cache and re-login**:
   - Clear session storage
   - Logout and login again
   - This refreshes the MSAL token cache

---

## Issue 2: "Network Error" in Frontend

**Symptom**: Frontend shows "Network Error - No response from server"

**Root Cause**: Backend is not running or not accessible.

### Fix Steps:

1. **Start the backend server**:
   ```bash
   cd backend
   uvicorn src.main:app --reload --port 8000
   ```

2. **Verify backend is running**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","version":"1.0.0"}
   ```

3. **Check CORS configuration**:
   - In `backend/.env`, ensure:
     ```
     ALLOWED_ORIGINS=http://localhost:3000
     ```
   - Restart backend after changing `.env`

4. **Verify frontend API URL**:
   - In `frontend/.env.local`, ensure:
     ```
     NEXT_PUBLIC_API_URL=http://localhost:8000
     ```
   - Restart frontend after changing `.env`

---

## Issue 3: AWS Authentication Errors

**Symptom**: Backend can't assume AWS roles or access Cognito

### Fix Steps:

1. **Configure AWS credentials**:
   ```bash
   aws configure
   # Enter your AWS Access Key ID and Secret Access Key
   ```

2. **Test AWS credentials**:
   ```bash
   aws sts get-caller-identity
   # Should return your AWS account info
   ```

3. **Create IAM roles in target accounts**:
   - See `AWS_AUTHENTICATION_SETUP.md` for detailed steps
   - Role name must match `ACCOUNT_ROLE_NAME` in `backend/.env`

4. **Set ALLOWED_ACCOUNTS**:
   ```bash
   # In backend/.env
   ALLOWED_ACCOUNTS=123456789012,987654321098
   ```

---

## Complete Setup Checklist

### Backend Setup:
- [ ] Backend server running on port 8000
- [ ] `backend/.env` configured with:
  - [ ] `ENTRA_ID_TENANT_ID`
  - [ ] `ENTRA_ID_CLIENT_ID`
  - [ ] `ENTRA_ID_AUDIENCE`
  - [ ] `ALLOWED_ACCOUNTS` (comma-separated account IDs)
  - [ ] `ACCOUNT_ROLE_NAME=CognitoManagementRole`
  - [ ] `ALLOWED_ORIGINS=http://localhost:3000`
- [ ] AWS credentials configured (`aws configure`)
- [ ] IAM roles created in target AWS accounts

### Frontend Setup:
- [ ] Frontend running on port 3000
- [ ] `frontend/.env.local` configured with:
  - [ ] `NEXT_PUBLIC_ENTRA_CLIENT_ID`
  - [ ] `NEXT_PUBLIC_ENTRA_TENANT_ID`
  - [ ] `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] User logged in via Entra ID
- [ ] JWT token present in session storage

### Testing:
- [ ] Backend health check works: `curl http://localhost:8000/health`
- [ ] Frontend can login and see dashboard
- [ ] API calls include `Authorization: Bearer <token>` header
- [ ] Accounts list loads without errors

---

## Debug Commands

### Check Backend Logs:
```bash
# Backend should show:
# - "Application startup complete"
# - Request logs when API is called
# - No authentication errors
```

### Check Frontend Console:
```javascript
// Open browser DevTools → Console
// Should see:
// - No CORS errors
// - No network errors
// - MSAL initialization messages
```

### Check Network Tab:
1. Open DevTools → Network tab
2. Make a request (e.g., navigate to Accounts page)
3. Check the request:
   - **Status**: Should be 200 (not 401 or 500)
   - **Request Headers**: Should have `Authorization: Bearer <token>`
   - **Response**: Should have JSON data (not error message)

---

## Still Having Issues?

1. **Check all environment variables** are set correctly
2. **Restart both frontend and backend** after changing `.env` files
3. **Clear browser cache and session storage**
4. **Check backend terminal** for detailed error messages
5. **Check browser console** for frontend errors
6. **Verify AWS credentials** with `aws sts get-caller-identity`

For detailed AWS setup, see `AWS_AUTHENTICATION_SETUP.md`.

