'use client'

import { ReactNode, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth, AppRole } from '@/lib/auth/useAuth'

interface ProtectedRouteProps {
  children: ReactNode
  /**
   * Roles required to access this route.
   * If omitted, only authentication is required.
   */
  requiredRoles?: readonly AppRole[]
}

export function ProtectedRoute({
  children,
  requiredRoles,
}: ProtectedRouteProps) {
  const router = useRouter()
  const { isAuthenticated, roles } = useAuth()

  useEffect(() => {
    // Not authenticated → redirect to login
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    // Role-based protection
    if (requiredRoles && requiredRoles.length > 0) {
      const hasRequiredRole = requiredRoles.some((role: AppRole) =>
        roles.includes(role)
      )

      if (!hasRequiredRole) {
        router.push('/dashboard')
      }
    }
  }, [isAuthenticated, roles, requiredRoles, router])

  return <>{children}</>
}
