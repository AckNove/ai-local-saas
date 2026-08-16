import { get, post, patch, del } from './client'
import type { Metrics, Reservation, VideoBinding, VideoBindingInput } from '../types'

// 数据看板 / 履约（预约、视频号挂载）接口封装。

/** 经营指标聚合；平台可传 merchant_id=0 或省略做跨商户汇总。 */
export function getMetrics(params?: {
  merchant_id?: number
  date_from?: string
  date_to?: string
}): Promise<Metrics> {
  return get<Metrics>('/dashboard/metrics', params)
}

// ---- 预约订座（T07） ----
export function listReservations(params?: {
  store_id?: number
  status?: string
  page?: number
  page_size?: number
}): Promise<{ list: Reservation[]; total: number; page: number; page_size: number }> {
  return get('/fulfillment/reservations', params)
}

export function updateReservation(id: number, status: string): Promise<Reservation> {
  return patch<Reservation>(`/fulfillment/reservations/${id}`, { status })
}

// ---- 视频号挂载（T08） ----
export function listVideoBindings(): Promise<{ list: VideoBinding[]; total: number; page: number; page_size: number }> {
  return get('/fulfillment/video-bindings')
}

export function createVideoBinding(body: VideoBindingInput): Promise<VideoBinding> {
  return post<VideoBinding>('/fulfillment/video-bindings', body)
}

export function deleteVideoBinding(id: number): Promise<{ id: number }> {
  return del<{ id: number }>(`/fulfillment/video-bindings/${id}`)
}
