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
      setError(null)
      const data = await getAccounts()
      setAccounts(data)
      
      if (data.length === 0) {
        setError('No AWS accounts configured. Please configure ALLOWED_ACCOUNTS in backend .env file.')
      }
    } catch (err: any) {
      console.error('Error loading accounts:', err)
      const errorMessage = err.response?.data?.error?.message || err.message || 'Failed to load accounts'
      setError(errorMessage)
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
    const isConnectionError = error.includes('Cannot connect') || error.includes('ERR_CONNECTION_REFUSED')
    
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800 font-semibold mb-2">Network Error</p>
        <p className="text-red-700 text-sm mb-4">{error}</p>
        {isConnectionError && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-yellow-800 font-semibold mb-2">Backend Not Running</p>
            <p className="text-yellow-700 text-sm mb-2">To fix this:</p>
            <ol className="list-decimal list-inside text-yellow-700 text-sm space-y-1">
              <li>Open a terminal and navigate to the <code className="bg-yellow-100 px-1 rounded">backend</code> directory</li>
              <li>Start the backend server: <code className="bg-yellow-100 px-1 rounded">uvicorn src.main:app --reload</code></li>
              <li>Verify it's running at: <code className="bg-yellow-100 px-1 rounded">http://localhost:8000</code></li>
              <li>Refresh this page</li>
            </ol>
          </div>
        )}
        <button
          onClick={loadAccounts}
          className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          Retry
        </button>
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

