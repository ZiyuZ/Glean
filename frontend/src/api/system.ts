import type { AuthStatusResponse, LoginResponse, SystemVersionResponse } from '../types/api'
import { apiClient } from './client'

/**
 * 获取系统版本信息
 */
export async function getSystemVersion(): Promise<SystemVersionResponse> {
  return apiClient.get('system/version').json<SystemVersionResponse>()
}

export async function checkAuthStatus(): Promise<AuthStatusResponse> {
  return apiClient.get('system/auth-status').json<AuthStatusResponse>()
}

export async function login(password: string): Promise<LoginResponse> {
  return apiClient.post('system/login', { json: { password } }).json<LoginResponse>()
}
