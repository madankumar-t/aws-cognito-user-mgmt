export interface User {
  username: string
  user_status: string
  enabled: boolean
  user_create_date?: string
  user_last_modified_date?: string
  attributes: Record<string, any>
  mfa_enabled: boolean
}

export interface CreateUserRequest {
  username: string
  email: string
  password?: string
  attributes?: Record<string, string>
  temporary_password?: boolean
}

