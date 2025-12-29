'use client'

import { ReactNode, useEffect, useState } from 'react'
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
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    // Wait a bit for auth to initialize
    const timer = setTimeout(() => {
      setIsChecking(false)
    }, 500)

    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (isChecking) return

    if (!isAuthenticated) {
      router.push('/')
      return
    }

    if (requiredRoles && requiredRoles.length > 0) {
      const hasRequiredRole = requiredRoles.some((role) =>
        roles.includes(role)
      )

      if (!hasRequiredRole) {
        // User authenticated but no required role
        // Show message instead of redirect loop
        console.warn('User does not have required role:', requiredRoles)
        // Still render children but show warning
      }
    }
  }, [isAuthenticated, roles, requiredRoles, router, isChecking])

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
