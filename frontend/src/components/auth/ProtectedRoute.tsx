'use client'

import { ReactNode, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth, AppRole } from '@/lib/auth/useAuth'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRoles?: readonly AppRole[]
}

export function ProtectedRoute({
  children,
  requiredRoles,
}: ProtectedRouteProps) {
  const router = useRouter()
  const { isAuthenticated, roles } = useAuth()

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    if (requiredRoles && requiredRoles.length > 0) {
      const hasRequiredRole = requiredRoles.some((role) =>
        roles.includes(role)
      )

      if (!hasRequiredRole) {
        router.push('/dashboard')
      }
    }
  }, [isAuthenticated, roles, requiredRoles, router])

  return <>{children}</>
}
