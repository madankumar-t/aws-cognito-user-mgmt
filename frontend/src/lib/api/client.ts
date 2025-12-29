import axios from 'axios'
import { PublicClientApplication } from '@azure/msal-browser'
import { msalConfig } from '@/lib/auth/msalConfig'

let msalInstance: PublicClientApplication | undefined

/**
 * Always returns an initialized MSAL instance.
 * Throws if called on the server or before init.
 */
function getMsalInstance(): PublicClientApplication {
  if (!msalInstance) {
    msalInstance = new PublicClientApplication(msalConfig)
  }
  return msalInstance
}

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})

apiClient.interceptors.request.use(
  async (config) => {
    try {
      const instance = getMsalInstance()
      const accounts = instance.getAllAccounts()

      if (accounts.length === 0) {
        return config
      }

      const response = await instance.acquireTokenSilent({
        account: accounts[0],
        scopes: ['openid', 'profile'],
      })

      config.headers.Authorization = `Bearer ${response.accessToken}`
      return config
    } catch (error) {
      console.error('Failed to attach access token', error)
      return config
    }
  },
  (error) => Promise.reject(error)
)

export default apiClient
