'use client'

import { useMsal, useIsAuthenticated, useAccount } from '@azure/msal-react'
import { loginRequest } from './msalConfig'
import { useEffect, useState } from 'react'

/**
 * Application roles
 */
export type AppRole = 'Admin' | 'Developer'

/**
 * Minimal Entra ID token claims we care about
 */
interface EntraIdTokenClaims {
  groups?: string[]
  roles?: string[]
}

export function useAuth() {
  const { instance } = useMsal()
  const isAuthenticated = useIsAuthenticated()
  const account = useAccount()

  const [token, setToken] = useState<string | null>(null)
  const [roles, setRoles] = useState<AppRole[]>([])

  useEffect(() => {
    if (!isAuthenticated || !account) {
      setToken(null)
      setRoles([])
      return
    }

    const loadAuthData = async () => {
      try {
        const accessToken = await getAccessToken()
        if (!accessToken) {
          console.warn('No access token available')
          return
        }

        setToken(accessToken)

        // 👇 IMPORTANT: explicitly type idTokenClaims
        const claims = account.idTokenClaims as EntraIdTokenClaims | undefined

        // Debug: Log claims to help troubleshoot
        if (process.env.NODE_ENV === 'development') {
          console.log('Token Claims:', {
            groups: claims?.groups,
            roles: claims?.roles,
            allClaims: claims
          })
        }

        // Prefer App Roles, fallback to Groups
        const rawValues: string[] = claims?.roles ?? claims?.groups ?? []

        const extractedRoles: AppRole[] = rawValues
          .map((value) => {
            if (value === 'cognito-admin') return 'Admin'
            if (value === 'cognito-developer') return 'Developer'
            return null
          })
          .filter((r): r is AppRole => r !== null)

        setRoles(extractedRoles)

        // Warn if no roles found
        if (extractedRoles.length === 0 && rawValues.length > 0) {
          console.warn('User has groups/roles but none match required roles:', rawValues)
        } else if (rawValues.length === 0) {
          console.warn('User has no groups or roles in token. Ensure app is configured to emit group/role claims.')
        }
      } catch (error) {
        console.error('Error loading auth data:', error)
      }
    }

    loadAuthData()
  }, [isAuthenticated, account, instance])

  const login = async () => {
    await instance.loginPopup(loginRequest)
  }

  const logout = async () => {
    await instance.logoutPopup()
    setToken(null)
    setRoles([])
  }

  const getAccessToken = async (): Promise<string | null> => {
    if (!account) return null

    try {
      const response = await instance.acquireTokenSilent({
        ...loginRequest,
        account,
      })
      return response.accessToken
    } catch {
      const response = await instance.acquireTokenPopup(loginRequest)
      return response.accessToken
    }
  }

  return {
    isAuthenticated,
    user: account,
    token,
    roles,
    login,
    logout,
    getAccessToken,
  }
}
