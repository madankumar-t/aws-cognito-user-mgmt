'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getPools } from '@/lib/api/pools'
import { Pool } from '@/types/pool'
import { useAccountStore } from '@/store/accountStore'

export default function PoolsPage() {
  const [pools, setPools] = useState<Pool[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const { selectedAccount, selectedRegion, setPool } = useAccountStore()

  useEffect(() => {
    if (!selectedAccount || !selectedRegion) {
      router.push('/dashboard/accounts')
      return
    }
    loadPools()
  }, [selectedAccount, selectedRegion, router])

  const loadPools = async () => {
    if (!selectedAccount || !selectedRegion) return

    try {
      setLoading(true)
      const data = await getPools(selectedAccount.id, selectedRegion)
      setPools(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load pools')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectPool = (pool: Pool) => {
    setPool(pool)
    router.push('/dashboard/users')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">{error}</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Select Cognito User Pool ({selectedRegion})
      </h2>
      {pools.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <p className="text-yellow-800">No Cognito User Pools found in this region.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pools.map((pool) => (
            <div
              key={pool.id}
              onClick={() => handleSelectPool(pool)}
              className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:border-primary-500 hover:shadow-md cursor-pointer transition-all"
            >
              <h3 className="text-lg font-semibold text-gray-900">{pool.name}</h3>
              <p className="text-sm text-gray-500 mt-1">Pool ID: {pool.id}</p>
              {pool.creation_date && (
                <p className="text-xs text-gray-400 mt-1">
                  Created: {new Date(pool.creation_date).toLocaleDateString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

