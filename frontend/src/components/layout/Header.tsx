'use client'

import { useAuth } from '@/lib/auth/useAuth'
import LogoutButton from '@/components/auth/LogoutButton'

export default function Header() {
  const { user, roles } = useAuth()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900">
              AWS Cognito User Management
            </h1>
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <div className="text-sm text-gray-700">
                <span className="font-medium">{user.name || user.username}</span>
                {roles.length > 0 && (
                  <span className="ml-2 text-xs text-gray-500">
                    ({roles.join(', ')})
                  </span>
                )}
              </div>
            )}
            <LogoutButton />
          </div>
        </div>
      </div>
    </header>
  )
}

