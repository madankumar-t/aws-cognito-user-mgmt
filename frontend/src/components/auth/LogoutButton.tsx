'use client'

import { useAuth } from '@/lib/auth/useAuth'

export default function LogoutButton() {
  const { logout } = useAuth()

  return (
    <button
      onClick={logout}
      className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
    >
      Sign Out
    </button>
  )
}

