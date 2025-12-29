'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAccountStore } from '@/store/accountStore'

const AWS_REGIONS = [
  'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
  'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1',
  'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-2',
  'ap-south-1', 'ca-central-1', 'sa-east-1',
]

export default function RegionsPage() {
  const router = useRouter()
  const { selectedAccount, setRegion } = useAccountStore()

  useEffect(() => {
    if (!selectedAccount) {
      router.push('/dashboard/accounts')
    }
  }, [selectedAccount, router])

  const handleSelectRegion = (region: string) => {
    setRegion(region)
    router.push('/dashboard/pools')
  }

  if (!selectedAccount) {
    return null
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Select AWS Region for {selectedAccount.name}
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {AWS_REGIONS.map((region) => (
          <button
            key={region}
            onClick={() => handleSelectRegion(region)}
            className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:border-primary-500 hover:shadow-md text-left transition-all"
          >
            <span className="font-medium text-gray-900">{region}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

