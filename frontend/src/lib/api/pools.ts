import apiClient from './client'
import { Pool } from '@/types/pool'

export async function getPools(accountId: string, region: string): Promise<Pool[]> {
  const response = await apiClient.get(
    `/api/v1/accounts/${accountId}/regions/${region}/pools`
  )
  return response.data
}

