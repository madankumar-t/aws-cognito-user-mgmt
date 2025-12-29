'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAccountStore } from '@/store/accountStore'

export default function DashboardPage() {
  const router = useRouter()
  const { selectedAccount, selectedRegion, selectedPool } = useAccountStore()

  useEffect(() => {
    // Redirect based on selection state
    if (!selectedAccount) {
      router.push('/dashboard/accounts')
    } else if (!selectedRegion) {
      router.push('/dashboard/regions')
    } else if (!selectedPool) {
      router.push('/dashboard/pools')
    } else {
      router.push('/dashboard/users')
    }
  }, [selectedAccount, selectedRegion, selectedPool, router])

  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  )
}
