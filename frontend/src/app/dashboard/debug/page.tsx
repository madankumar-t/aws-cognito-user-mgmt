'use client'

import { useAuth } from '@/lib/auth/useAuth'

/**
 * Debug page to check authentication state
 * Access at: /dashboard/debug
 * Remove this file in production
 */
export default function DebugPage() {
  const { isAuthenticated, user, roles, token } = useAuth()

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Authentication Debug Info</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-sm space-y-4">
        <div>
          <h2 className="font-semibold">Authentication Status</h2>
          <p>Is Authenticated: {isAuthenticated ? '✅ Yes' : '❌ No'}</p>
        </div>

        <div>
          <h2 className="font-semibold">User Info</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-auto">
            {JSON.stringify(user, null, 2)}
          </pre>
        </div>

        <div>
          <h2 className="font-semibold">Roles</h2>
          <p>Roles: {roles.length > 0 ? roles.join(', ') : 'None'}</p>
          <p>Has Admin: {roles.includes('Admin') ? '✅' : '❌'}</p>
          <p>Has Developer: {roles.includes('Developer') ? '✅' : '❌'}</p>
        </div>

        <div>
          <h2 className="font-semibold">Token Claims</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-auto text-xs">
            {user?.idTokenClaims ? JSON.stringify(user.idTokenClaims, null, 2) : 'No claims'}
          </pre>
        </div>

        <div>
          <h2 className="font-semibold">Groups (from token)</h2>
          <p>
            {user?.idTokenClaims?.groups 
              ? `Groups: ${user.idTokenClaims.groups.join(', ')}`
              : 'No groups in token'}
          </p>
        </div>

        <div>
          <h2 className="font-semibold">App Roles (from token)</h2>
          <p>
            {user?.idTokenClaims?.roles 
              ? `Roles: ${user.idTokenClaims.roles.join(', ')}`
              : 'No roles in token'}
          </p>
        </div>

        <div>
          <h2 className="font-semibold">Token (first 50 chars)</h2>
          <p className="text-xs break-all">
            {token ? `${token.substring(0, 50)}...` : 'No token'}
          </p>
        </div>

        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <h3 className="font-semibold text-yellow-800">Expected Configuration</h3>
          <ul className="list-disc list-inside text-sm text-yellow-700 mt-2">
            <li>User should be in group: <code>cognito-admin</code> or <code>cognito-developer</code></li>
            <li>OR user should have app role: <code>cognito-admin</code> or <code>cognito-developer</code></li>
            <li>App must be configured to emit group/role claims in token</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

