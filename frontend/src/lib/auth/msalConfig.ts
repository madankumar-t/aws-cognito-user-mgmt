import { Configuration } from '@azure/msal-browser'

/**
 * MSAL configuration (SAFE for Next.js build)
 * ❌ No window usage
 * ❌ No document usage
 */
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_ENTRA_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_ENTRA_TENANT_ID}`,
    redirectUri: '/',            // SAFE: no window
    postLogoutRedirectUri: '/',
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
}

/**
 * Scopes requested during login / token acquisition
 * Used by useAuth() and API client
 */
export const loginRequest = {
  scopes: ['openid', 'profile', 'email'],
}
