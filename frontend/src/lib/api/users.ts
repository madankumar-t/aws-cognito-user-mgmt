import apiClient from './client'
import { User, CreateUserRequest } from '@/types/user'

export interface ListUsersParams {
  poolId: string
  accountId: string
  region: string
  page?: number
  limit?: number
  search?: string
  status?: string
}

export interface UserListResponse {
  users: User[]
  pagination: {
    page: number
    limit: number
    total: number
    next_token?: string
  }
}

export async function getUsers(params: ListUsersParams): Promise<UserListResponse> {
  const response = await apiClient.get(`/api/v1/pools/${params.poolId}/users`, {
    params: {
      account_id: params.accountId,
      region: params.region,
      page: params.page,
      limit: params.limit,
      search: params.search,
      status: params.status,
    },
  })
  return response.data
}

export async function getUser(
  poolId: string,
  username: string,
  accountId: string,
  region: string
): Promise<User> {
  const response = await apiClient.get(`/api/v1/pools/${poolId}/users/${username}`, {
    params: { account_id: accountId, region },
  })
  return response.data
}

export async function createUser(
  poolId: string,
  userData: CreateUserRequest,
  accountId: string,
  region: string
): Promise<User> {
  const response = await apiClient.post(`/api/v1/pools/${poolId}/users`, userData, {
    params: { account_id: accountId, region },
  })
  return response.data.user
}

export async function updateUserStatus(
  poolId: string,
  username: string,
  enabled: boolean,
  accountId: string,
  region: string
): Promise<User> {
  const response = await apiClient.patch(
    `/api/v1/pools/${poolId}/users/${username}/status`,
    { enabled },
    { params: { account_id: accountId, region } }
  )
  return response.data
}

export async function setPassword(
  poolId: string,
  username: string,
  password: string,
  permanent: boolean,
  accountId: string,
  region: string
): Promise<void> {
  await apiClient.put(
    `/api/v1/pools/${poolId}/users/${username}/password`,
    { password, permanent },
    { params: { account_id: accountId, region } }
  )
}

export async function resetPassword(
  poolId: string,
  username: string,
  accountId: string,
  region: string
): Promise<void> {
  await apiClient.post(
    `/api/v1/pools/${poolId}/users/${username}/reset-password`,
    {},
    { params: { account_id: accountId, region } }
  )
}

export async function forcePasswordReset(
  poolId: string,
  username: string,
  accountId: string,
  region: string
): Promise<void> {
  await apiClient.post(
    `/api/v1/pools/${poolId}/users/${username}/force-password-reset`,
    {},
    { params: { account_id: accountId, region } }
  )
}

