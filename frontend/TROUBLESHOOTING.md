# Troubleshooting Guide
## Blank Screen After Login

---

## Issue: Blank Screen After Successful Microsoft Login

### Symptoms
- ✅ Login to Microsoft works successfully
- ✅ Redirects back to application
- ❌ Blank screen appears at `/dashboard`

---

## Root Causes & Solutions

### 1. Missing Roles/Groups Configuration

**Problem**: User is authenticated but doesn't have required roles (`Admin` or `Developer`)

**Solution**: Configure roles in Microsoft Entra ID

#### Option A: Using Groups (Recommended)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **Groups**
3. Create two security groups:
   - **Group Name**: `cognito-admin`
   - **Group Name**: `cognito-developer`
4. Add your user to one of these groups
5. **Important**: Configure the app to receive group claims:
   - Go to **App registrations** → Your app → **Token configuration**
   - Click **Add groups claim**
   - Select **Security groups** or **All groups**
   - Click **Add**

#### Option B: Using App Roles

1. Go to **App registrations** → Your app → **App roles**
2. Create roles:
   - Display name: `Cognito Admin`, Value: `cognito-admin`
   - Display name: `Cognito Developer`, Value: `cognito-developer`
3. Assign users to roles:
   - Go to **Enterprise applications** → Your app → **Users and groups**
   - Assign users to appropriate roles

### 2. Missing API URL Configuration

**Problem**: `NEXT_PUBLIC_API_URL` not set, causing API calls to fail

**Solution**: 
1. Check if `.env.local` exists in `frontend/` directory
2. Add:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Restart the development server

### 3. Redirect URI Mismatch

**Problem**: Redirect URI in Azure AD doesn't match application

**Solution**:
1. In Azure Portal → **App registrations** → Your app → **Authentication**
2. Under **Single-page application**, ensure you have:
   - `http://localhost:3000` (for development)
   - `https://your-domain.com` (for production)
3. The redirect URI in code uses `window.location.origin` which should match

### 4. Browser Console Errors

**Check browser console** (F12 → Console tab) for errors:

- **401 Unauthorized**: Backend not running or API URL incorrect
- **CORS errors**: Backend CORS not configured correctly
- **Token errors**: MSAL configuration issue

---

## Debugging Steps

### Step 1: Check Browser Console

Open browser DevTools (F12) and check:
- **Console tab**: Look for errors
- **Network tab**: Check if API calls are failing
- **Application tab**: Check if tokens are stored

### Step 2: Verify Environment Variables

```bash
# In frontend directory
cat .env.local

# Should show:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_ENTRA_TENANT_ID=your-tenant-id
# NEXT_PUBLIC_ENTRA_CLIENT_ID=your-client-id
```

### Step 3: Check Authentication State

Add temporary debug code to see what's happening:

```typescript
// In useAuth hook or dashboard layout
console.log('Auth State:', {
  isAuthenticated,
  roles,
  user: account?.name,
  groups: account?.idTokenClaims?.groups,
  allClaims: account?.idTokenClaims
})
```

### Step 4: Verify Backend is Running

```bash
# Test backend health
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","version":"1.0.0"}
```

### Step 5: Check Role Extraction

The app looks for:
- Groups: `cognito-admin` or `cognito-developer`
- OR App Roles: `cognito-admin` or `cognito-developer`

Verify in browser console what groups/roles are in the token.

---

## Quick Fixes

### Fix 1: Temporarily Remove Role Requirement

To test if roles are the issue, temporarily modify `dashboard/layout.tsx`:

```typescript
// Comment out role check temporarily
// const hasRequiredRole = roles.includes('Admin') || roles.includes('Developer')
// if (!hasRequiredRole && roles.length > 0) { ... }

// Just check authentication
if (!isAuthenticated) {
  router.push('/')
  return
}
```

### Fix 2: Add Debug Information

Add this to `dashboard/layout.tsx` to see what's happening:

```typescript
useEffect(() => {
  console.log('Dashboard Layout State:', {
    isAuthenticated,
    roles,
    hasRoles: roles.length > 0
  })
}, [isAuthenticated, roles])
```

### Fix 3: Check if API is Accessible

Test if the accounts API works:

```bash
# Get token from browser (Application tab → Session Storage)
# Then test:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/accounts
```

---

## Common Configuration Issues

### Issue: "User does not have required role"

**Cause**: User not in `cognito-admin` or `cognito-developer` group/role

**Fix**: 
1. Add user to group in Azure AD
2. Configure app to emit group claims
3. Wait a few minutes for changes to propagate
4. Log out and log back in

### Issue: "Invalid client" or "AADSTS700016"

**Cause**: Client ID incorrect or app not found

**Fix**: 
1. Verify `NEXT_PUBLIC_ENTRA_CLIENT_ID` matches Azure Portal
2. Check app exists in correct tenant
3. Verify app registration is active

### Issue: "Redirect URI mismatch" (AADSTS50011)

**Cause**: Redirect URI in Azure AD doesn't match

**Fix**:
1. Azure Portal → App registrations → Your app → Authentication
2. Add exact redirect URI: `http://localhost:3000`
3. Save and wait a few minutes

---

## Verification Checklist

After fixing issues, verify:

- [ ] User can log in successfully
- [ ] User is redirected to `/dashboard` after login
- [ ] Dashboard shows header with user name
- [ ] Dashboard shows sidebar navigation
- [ ] User can see "Accounts" page
- [ ] No errors in browser console
- [ ] API calls work (check Network tab)

---

## Still Having Issues?

1. **Check browser console** for specific error messages
2. **Verify all environment variables** are set correctly
3. **Test backend API** independently
4. **Check Azure AD configuration** matches requirements
5. **Review network requests** in DevTools Network tab

---

## Need More Help?

1. Enable debug logging in browser console
2. Check CloudWatch Logs (if backend deployed)
3. Verify token claims in browser (Application → Session Storage)
4. Test with a user who has Admin role

---

**Last Updated**: 2024

