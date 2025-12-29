# Frontend Environment Variables Setup
## Microsoft Entra ID Configuration

---

## 📍 Where to Configure

### Step 1: Create `.env.local` File

In the `frontend/` directory, create a file named `.env.local`:

```bash
cd frontend
touch .env.local  # or create manually
```

### Step 2: Add Your Entra ID Details

Open `.env.local` and add the following:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Microsoft Entra ID Configuration
NEXT_PUBLIC_ENTRA_TENANT_ID=your-tenant-id-here
NEXT_PUBLIC_ENTRA_CLIENT_ID=your-client-id-here
```

---

## 🔑 Required Variables

### 1. `NEXT_PUBLIC_ENTRA_TENANT_ID`

**What**: Your Microsoft Entra ID Tenant ID (Directory ID)

**Where to find**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory**
3. Click **Overview** (in the left sidebar)
4. Copy the **Tenant ID** (it's a GUID like: `12345678-1234-1234-1234-123456789abc`)

**Example**:
```bash
NEXT_PUBLIC_ENTRA_TENANT_ID=12345678-1234-1234-1234-123456789abc
```

### 2. `NEXT_PUBLIC_ENTRA_CLIENT_ID`

**What**: Your Azure AD Application (Client) ID

**Where to find**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click on your application (or create a new one)
4. In the **Overview** page, copy the **Application (client) ID**

**Example**:
```bash
NEXT_PUBLIC_ENTRA_CLIENT_ID=87654321-4321-4321-4321-cba987654321
```

### 3. `NEXT_PUBLIC_API_URL`

**What**: Your backend API URL

**For local development**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**For production**:
```bash
NEXT_PUBLIC_API_URL=https://your-api-url.execute-api.us-east-1.amazonaws.com/prod
```

---

## 📝 Complete Example

Your `frontend/.env.local` file should look like this:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Microsoft Entra ID - Tenant ID (Directory ID)
NEXT_PUBLIC_ENTRA_TENANT_ID=12345678-1234-1234-1234-123456789abc

# Microsoft Entra ID - Client ID (Application ID)
NEXT_PUBLIC_ENTRA_CLIENT_ID=87654321-4321-4321-4321-cba987654321
```

---

## ✅ Quick Setup Steps

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Create `.env.local` file**:
   ```bash
   # On Windows (PowerShell)
   New-Item -Path .env.local -ItemType File
   
   # On Linux/Mac
   touch .env.local
   ```

3. **Add your values** (use any text editor):
   ```bash
   # Copy the example above and replace with your actual values
   ```

4. **Restart development server**:
   ```bash
   # Stop current server (Ctrl+C) and restart
   npm run dev
   ```

5. **Test**:
   - Open http://localhost:3000
   - Click "Sign in with Microsoft"
   - Should redirect to Microsoft login

---

## 🔍 How It's Used

The environment variables are automatically loaded by Next.js and used in:

**File**: `frontend/src/lib/auth/msalConfig.ts`

```typescript
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_ENTRA_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_ENTRA_TENANT_ID}`,
    redirectUri: '/',
    postLogoutRedirectUri: '/',
  },
  // ...
}
```

---

## 🚨 Important Notes

1. **File Name**: Must be `.env.local` (not `.env` or `.env.example`)
2. **Variable Prefix**: All variables must start with `NEXT_PUBLIC_` to be accessible in the browser
3. **Restart Required**: After changing `.env.local`, restart the Next.js dev server
4. **Never Commit**: `.env.local` is in `.gitignore` - never commit it to version control
5. **No Spaces**: Don't put spaces around the `=` sign

---

## 🚨 Troubleshooting

### Variables not loading?
- ✅ Check file is named `.env.local` (exact name)
- ✅ Check variables start with `NEXT_PUBLIC_`
- ✅ Restart the dev server (`npm run dev`)
- ✅ Check for typos in variable names

### "Invalid client" error?
- ✅ Verify `NEXT_PUBLIC_ENTRA_CLIENT_ID` is correct
- ✅ Check the app exists in Azure AD
- ✅ Ensure you're using the correct tenant

### "Redirect URI mismatch" error?
- ✅ In Azure Portal → App Registrations → Your App → Authentication
- ✅ Add redirect URI: `http://localhost:3000` (for development)
- ✅ Add redirect URI: `https://your-domain.com` (for production)

---

## 📋 For Production Deployment

When deploying to production (Vercel, AWS Amplify, etc.), set the same environment variables in your hosting platform's environment variable settings.

**Vercel**:
1. Go to Project Settings → Environment Variables
2. Add each variable with the same names
3. Set values for Production, Preview, and Development

**AWS Amplify**:
1. Go to App Settings → Environment Variables
2. Add each variable
3. Redeploy

---

## 📚 Additional Resources

- See `ENTRA_ID_SETUP.md` for detailed Azure AD setup
- [Azure Portal](https://portal.azure.com)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)

---

**Quick Reference**: Create `frontend/.env.local` with your Tenant ID and Client ID!

