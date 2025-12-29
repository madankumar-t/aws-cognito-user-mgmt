import axios from 'axios'
import { PublicClientApplication } from '@azure/msal-browser'
import { msalConfig, loginRequest } from '@/lib/auth/msalConfig'

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
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000, // 10 second timeout
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
        scopes: loginRequest.scopes, // Use scopes from loginRequest
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

// Response interceptor for better error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.message.includes('ERR_CONNECTION_REFUSED')) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      error.message = `Cannot connect to backend API at ${apiUrl}. Please ensure the backend server is running.`
    } else if (error.response) {
      // Server responded with error status
      error.message = error.response.data?.error?.message || error.message
    } else if (error.request) {
      // Request made but no response
      error.message = 'No response from server. Please check if the backend is running.'
    }
    return Promise.reject(error)
  }
)

export default apiClient
