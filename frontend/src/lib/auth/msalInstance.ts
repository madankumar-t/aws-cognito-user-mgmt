import { PublicClientApplication } from '@azure/msal-browser'
import { msalConfig } from './msalConfig'

export const msalInstance = new PublicClientApplication(msalConfig)

// Initialize MSAL
msalInstance.initialize().then(() => {
  // Handle redirect response
  msalInstance.handleRedirectPromise()
})

