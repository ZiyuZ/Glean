/**
 * 扫描相关 API
 */

import type {
  ScanResponse,
  ScanStatusResponse,
  StopScanResponse,
} from '../types/api'
import { apiClient } from './client'

/**
 * 触发目录扫描
 */
export async function triggerScan(fullScan = false): Promise<ScanResponse> {
  const searchParams = new URLSearchParams()
  if (fullScan) {
    searchParams.append('full_scan', 'true')
  }

  return apiClient.post('scan', { searchParams }).json<ScanResponse>()
}

/**
 * 获取扫描状态
 */
export async function getScanStatus(): Promise<ScanStatusResponse> {
  return apiClient.get('scan/status').json<ScanStatusResponse>()
}

/**
 * 停止正在进行的扫描
 */
export async function stopScan(): Promise<StopScanResponse> {
  return apiClient.post('scan/stop').json<StopScanResponse>()
}
