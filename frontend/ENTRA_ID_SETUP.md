# Microsoft Entra ID Configuration Guide
## Frontend Setup

This guide explains where and how to configure Microsoft Entra ID details in the frontend application.

---

## 📍 Where to Configure

### Option 1: Environment Variables File (Recommended)

Create a `.env.local` file in the `frontend/` directory:

```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your values
```

### Option 2: Deployment Platform Environment Variables

For production deployments, set environment variables in your hosting platform:
- **Vercel**: Project Settings → Environment Variables
- **AWS Amplify**: App Settings → Environment Variables
- **Netlify**: Site Settings → Environment Variables

---

## 🔑 Required Environment Variables

### 1. `NEXT_PUBLIC_ENTRA_TENANT_ID`

**What it is**: Your Microsoft Entra ID (Azure AD) Tenant ID

**Where to find it**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory**
3. Click **Overview**
4. Copy the **Tenant ID**

**Example**:
```bash
NEXT_PUBLIC_ENTRA_TENANT_ID=12345678-1234-1234-1234-123456789abc
```

### 2. `NEXT_PUBLIC_ENTRA_CLIENT_ID`

**What it is**: Your Azure AD Application (Client) ID

**Where to find it**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Select your application
4. Click **Overview**
5. Copy the **Application (client) ID**

**Example**:
```bash
NEXT_PUBLIC_ENTRA_CLIENT_ID=87654321-4321-4321-4321-cba987654321
```

### 3. `NEXT_PUBLIC_API_URL` (Also Required)

**What it is**: Your backend API URL

**For local development**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**For production**:
```bash
NEXT_PUBLIC_API_URL=https://your-api-url.execute-api.us-east-1.amazonaws.com/prod
```

---

## 📝 Complete .env.local Example

Create `frontend/.env.local` with these values:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Microsoft Entra ID Configuration
NEXT_PUBLIC_ENTRA_TENANT_ID=12345678-1234-1234-1234-123456789abc
NEXT_PUBLIC_ENTRA_CLIENT_ID=87654321-4321-4321-4321-cba987654321
```

---

## 🔍 How It's Used

The environment variables are used in `frontend/src/lib/auth/msalConfig.ts`:

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

## ✅ Verification Steps

1. **Create `.env.local` file**:
   ```bash
   cd frontend
   cp .env.example .env.local
   ```

2. **Add your values**:
   ```bash
   # Edit .env.local
   nano .env.local  # or use your preferred editor
   ```

3. **Restart development server**:
   ```bash
   # Stop the server (Ctrl+C)
   npm run dev
   ```

4. **Test authentication**:
   - Open http://localhost:3000
   - Click "Sign in with Microsoft"
   - You should be redirected to Microsoft login

---

## 🚨 Common Issues

### Issue: "Invalid client" error
**Solution**: 
- Verify `NEXT_PUBLIC_ENTRA_CLIENT_ID` is correct
- Check that the app is registered in Azure AD
- Ensure the app registration is in the correct tenant

### Issue: "AADSTS50011: Redirect URI mismatch"
**Solution**:
- In Azure Portal → App Registrations → Your App → Authentication
- Add redirect URI: `http://localhost:3000` (for development)
- Add redirect URI: `https://your-domain.com` (for production)
- The redirect URI in code is set to `/` which works with Next.js routing

### Issue: Environment variables not loading
**Solution**:
- Ensure file is named `.env.local` (not `.env`)
- Restart the Next.js development server
- Check that variable names start with `NEXT_PUBLIC_`
- Verify no typos in variable names

### Issue: "Tenant not found"
**Solution**:
- Verify `NEXT_PUBLIC_ENTRA_TENANT_ID` is correct
- Check that you're using the correct tenant ID
- Ensure the tenant ID format is correct (GUID format)

---

## 📋 Quick Checklist

- [ ] Created `.env.local` file in `frontend/` directory
- [ ] Added `NEXT_PUBLIC_ENTRA_TENANT_ID` with your tenant ID
- [ ] Added `NEXT_PUBLIC_ENTRA_CLIENT_ID` with your client ID
- [ ] Added `NEXT_PUBLIC_API_URL` with backend URL
- [ ] Restarted development server
- [ ] Tested login flow
- [ ] Configured redirect URIs in Azure AD

---

## 🔐 Security Notes

1. **Never commit `.env.local`** to version control
   - It's already in `.gitignore`
   - Contains sensitive information

2. **Use different values for development and production**
   - Development: Use test Azure AD app
   - Production: Use production Azure AD app

3. **Rotate credentials regularly**
   - Update environment variables when credentials change
   - Update in both local and deployment environments

---

## 📚 Additional Resources

- [Azure Portal](https://portal.azure.com)
- [Microsoft Entra ID Documentation](https://learn.microsoft.com/en-us/entra/identity-platform/)
- [MSAL.js Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js)

---

**Last Updated**: 2024

