import type { SystemVersionResponse } from '../types/api'
import { apiClient } from './client'

/**
 * 获取系统版本信息
 */
export async function getSystemVersion(): Promise<SystemVersionResponse> {
  return apiClient.get('system/version').json<SystemVersionResponse>()
}
