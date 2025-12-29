# Microsoft Entra ID (Azure AD) Configuration Guide
## Complete Setup for Frontend Application

---

## ⚠️ Important: No Secret Key Needed for SPA

**For Single Page Applications (SPA), you do NOT need to configure client secrets.**

The application uses **Public Client Authentication** which is designed for browser-based apps that cannot securely store secrets.

---

## Step-by-Step Azure AD Configuration

### Step 1: Register Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Fill in:
   - **Name**: `AWS Cognito Management App` (or your choice)
   - **Supported account types**: 
     - Choose based on your needs:
       - "Accounts in this organizational directory only" (Single tenant)
       - "Accounts in any organizational directory" (Multi-tenant)
   - **Redirect URI**: 
     - **Platform**: Select **Single-page application (SPA)**
     - **URI**: `http://localhost:3000` (for development)
5. Click **Register**
6. **Note these values**:
   - **Application (client) ID** → This is your `NEXT_PUBLIC_ENTRA_CLIENT_ID`
   - **Directory (tenant) ID** → This is your `NEXT_PUBLIC_ENTRA_TENANT_ID`

### Step 2: Configure Authentication

1. In your app registration, go to **Authentication**
2. Under **Single-page application**, verify:
   - Redirect URI: `http://localhost:3000`
3. **Add additional redirect URIs** for production:
   - Click **Add URI**
   - Add: `https://your-domain.com` (your production URL)
4. Under **Implicit grant and hybrid flows**:
   - ✅ **ID tokens** (used for signing in users)
   - ❌ **Access tokens** (not needed for this flow)
5. Click **Save**

### Step 3: Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Add the following permissions:
   - `openid` (usually already added)
   - `profile` (usually already added)
   - `email` (usually already added)
   - `User.Read`
6. Click **Add permissions**
7. **Important**: Click **Grant admin consent for [Your Organization]**
   - This allows all users in your organization to use the app

### Step 4: Configure Groups/Roles (Choose One Method)

#### Method A: Using Security Groups (Recommended)

1. **Create Groups**:
   - Go to **Azure Active Directory** → **Groups**
   - Click **New group**
   - Create two groups:
     - **Group 1**:
       - Group type: **Security**
       - Group name: `cognito-admin`
       - Description: `Full access to Cognito user management`
     - **Group 2**:
       - Group type: **Security**
       - Group name: `cognito-developer`
       - Description: `Read-only access to Cognito user management`
   - Click **Create**

2. **Add Users to Groups**:
   - Open each group
   - Click **Members** → **Add members**
   - Add users who should have that role

3. **Configure App to Emit Group Claims**:
   - Go to **App registrations** → Your app → **Token configuration**
   - Click **Add groups claim**
   - Select:
     - **Security groups** (recommended) OR
     - **All groups** (if you want all groups)
   - Under **ID token**, check the box
   - Click **Add**
   - **Important**: If you have more than 200 groups, also select:
     - ✅ "Limit groups to groups assigned to the application"

#### Method B: Using App Roles

1. **Create App Roles**:
   - Go to **App registrations** → Your app → **App roles**
   - Click **Create app role**
   - **Role 1**:
     - Display name: `Cognito Admin`
     - Allowed member types: **Users/Groups**
     - Value: `cognito-admin`
     - Description: `Full access to Cognito user management`
   - Click **Apply**
   - **Role 2**:
     - Display name: `Cognito Developer`
     - Allowed member types: **Users/Groups**
     - Value: `cognito-developer`
     - Description: `Read-only access to Cognito user management`
   - Click **Apply**

2. **Assign Users to Roles**:
   - Go to **Enterprise applications** → Your app → **Users and groups**
   - Click **Add user/group**
   - Select users and assign them to `Cognito Admin` or `Cognito Developer` role
   - Click **Assign**

3. **Configure App to Emit Role Claims**:
   - Go to **App registrations** → Your app → **Token configuration**
   - Click **Add optional claim**
   - Select **ID token**
   - Check **roles**
   - Click **Add**

### Step 5: Configure Frontend Environment Variables

Create `frontend/.env.local`:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Microsoft Entra ID Configuration
NEXT_PUBLIC_ENTRA_TENANT_ID=your-tenant-id-from-step-1
NEXT_PUBLIC_ENTRA_CLIENT_ID=your-client-id-from-step-1
```

---

## Verification Checklist

After configuration, verify:

- [ ] App registered in Azure AD
- [ ] Redirect URI configured: `http://localhost:3000`
- [ ] API permissions granted and admin consent given
- [ ] Groups created: `cognito-admin` and `cognito-developer`
- [ ] OR App roles created: `cognito-admin` and `cognito-developer`
- [ ] Users added to groups/roles
- [ ] Token configuration set to emit groups/roles
- [ ] Frontend `.env.local` configured
- [ ] Backend running and accessible

---

## Testing the Configuration

1. **Start frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Open browser**: http://localhost:3000

3. **Click "Sign in with Microsoft"**

4. **Check browser console** (F12):
   - Should see token claims logged
   - Check for groups/roles in token

5. **Access debug page**: http://localhost:3000/dashboard/debug
   - Shows authentication state
   - Shows groups/roles from token
   - Helps troubleshoot issues

---

## Common Issues

### Issue: "User does not have required role"

**Cause**: User not in group/role OR groups/roles not in token

**Solution**:
1. Verify user is in `cognito-admin` or `cognito-developer` group/role
2. Check Token configuration → Groups claim is enabled
3. Wait 5-10 minutes for changes to propagate
4. Log out and log back in
5. Check debug page to see what's in the token

### Issue: "Redirect URI mismatch" (AADSTS50011)

**Cause**: Redirect URI in Azure AD doesn't match

**Solution**:
1. Azure Portal → App registrations → Your app → Authentication
2. Under "Single-page application", ensure `http://localhost:3000` is listed
3. Save changes
4. Wait a few minutes

### Issue: Groups/Roles not in token

**Cause**: Token configuration not set up correctly

**Solution**:
1. Go to Token configuration
2. Ensure "Groups" or "Roles" claim is added
3. Ensure "ID token" is checked
4. Save and wait for changes to propagate
5. Log out and log back in

---

## Security Notes

✅ **No Client Secret Needed**: SPAs use public client authentication  
✅ **Groups/Roles in Token**: Configured via Token configuration  
✅ **Redirect URIs**: Must match exactly (including protocol)  
✅ **Admin Consent**: Required for organization-wide access  

---

## Next Steps

After Azure AD is configured:

1. Configure frontend `.env.local` with Tenant ID and Client ID
2. Start backend: `cd backend && uvicorn src.main:app --reload`
3. Start frontend: `cd frontend && npm run dev`
4. Test login flow
5. Check debug page if issues occur

---

**Last Updated**: 2024

