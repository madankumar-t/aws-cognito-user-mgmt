# Frontend Deployment Notes

## Build Configuration

This application uses **client-side features** (authentication, state management, API calls) and should **NOT** be built with static export.

## Recommended Deployment Options

### ✅ Option 1: Vercel (Recommended)
- **No special configuration needed**
- Just run: `vercel --prod`
- Vercel handles Next.js automatically

### ✅ Option 2: AWS Amplify
- Connect GitHub repository
- Amplify auto-detects Next.js
- Configure environment variables in Amplify console

### ✅ Option 3: Netlify
- Connect repository
- Build command: `npm run build`
- Publish directory: `.next`
- Netlify handles Next.js automatically

### ✅ Option 4: Standalone Server
If deploying to a server (EC2, Docker, etc.):

```bash
# Build
npm run build

# Start server
npm start
```

Update `next.config.js`:
```js
output: 'standalone'
```

### ❌ Option 5: Static Export (NOT RECOMMENDED)
Static export (`next export`) **will NOT work** for this application because:
- Requires client-side JavaScript for authentication
- Uses browser APIs (MSAL, sessionStorage)
- Requires dynamic routing
- Needs API calls at runtime

If you absolutely need static hosting (S3/CloudFront), you would need to:
1. Convert to a pure client-side SPA
2. Handle routing client-side only
3. Remove server-side features
4. This is **not recommended** and would require significant refactoring

## Build Commands

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm start  # For standalone server
```

### Deploy to Vercel
```bash
vercel --prod
```

## Environment Variables

Make sure to set these in your deployment platform:
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_ENTRA_ID_TENANT_ID`
- `NEXT_PUBLIC_ENTRA_ID_CLIENT_ID`
- `NEXT_PUBLIC_ENTRA_ID_AUTHORITY`
- `NEXT_PUBLIC_ENTRA_ID_REDIRECT_URI`

## Troubleshooting

**Error: "Export encountered errors"**
- Solution: Don't use `next export` or `output: 'export'`
- Use one of the recommended deployment options above

**Error: "use client" directive issues**
- This is normal - the app uses client components
- Ensure you're not trying to do static export

**Build succeeds but app doesn't work**
- Check environment variables are set
- Verify API URL is correct
- Check browser console for errors

