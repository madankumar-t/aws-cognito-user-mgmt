'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getAccounts } from '@/lib/api/accounts'
import { Account } from '@/types/account'
import { useAccountStore } from '@/store/accountStore'

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const { setAccount } = useAccountStore()

  useEffect(() => {
    loadAccounts()
  }, [])

  const loadAccounts = async () => {
    try {
      setLoading(true)
      const data = await getAccounts()
      setAccounts(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load accounts')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectAccount = (account: Account) => {
    setAccount(account)
    router.push('/dashboard/regions')
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
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Select AWS Account</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {accounts.map((account) => (
          <div
            key={account.id}
            onClick={() => handleSelectAccount(account)}
            className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:border-primary-500 hover:shadow-md cursor-pointer transition-all"
          >
            <h3 className="text-lg font-semibold text-gray-900">{account.name}</h3>
            <p className="text-sm text-gray-500 mt-1">Account ID: {account.id}</p>
            <p className="text-sm text-gray-500 mt-1">
              {account.regions.length} region(s) available
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

