export const dynamic = 'force-dynamic'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute requiredRoles={['Admin', 'Developer']}>
      {children}
    </ProtectedRoute>
  )
}
