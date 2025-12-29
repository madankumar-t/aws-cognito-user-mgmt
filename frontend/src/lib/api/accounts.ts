import apiClient from './client'
import { Account } from '@/types/account'

export async function getAccounts(): Promise<Account[]> {
  const response = await apiClient.get('/api/v1/accounts')
  return response.data
}

export async function assumeRole(accountId: string, region: string): Promise<void> {
  await apiClient.post(`/api/v1/accounts/${accountId}/assume-role`, { region })
}

