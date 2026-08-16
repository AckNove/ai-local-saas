import { get, post, patch, del } from './client'
import type { PageResult, Merchant, Staff, StaffInput } from '../types'

// 租户资源接口封装（商户 / 员工）。

export function listMerchants(params?: {
  page?: number
  page_size?: number
}): Promise<PageResult<Merchant>> {
  return get<PageResult<Merchant>>('/tenants/merchants', params)
}

export function createMerchant(body: { name: string; logo_url?: string; contact_phone?: string; merchant_code?: string }): Promise<Merchant> {
  return post<Merchant>('/tenants/merchants', body)
}

export function updateMerchant(id: number, body: Partial<{ name: string; logo_url?: string; contact_phone?: string; merchant_code?: string; status?: string }>): Promise<Merchant> {
  return patch<Merchant>(`/tenants/merchants/${id}`, body)
}

export function deleteMerchant(id: number): Promise<{ deleted: boolean }> {
  return del<{ deleted: boolean }>(`/tenants/merchants/${id}`)
}

export function listStaff(params?: {
  store_id?: number
  page?: number
  page_size?: number
}): Promise<PageResult<Staff>> {
  return get<PageResult<Staff>>('/tenants/staff', params)
}

export function createStaff(body: StaffInput): Promise<Staff> {
  return post<Staff>('/tenants/staff', body)
}

export function updateStaff(id: number, body: Partial<StaffInput>): Promise<Staff> {
  return patch<Staff>(`/tenants/staff/${id}`, body)
}

export function deleteStaff(id: number): Promise<{ deleted: boolean }> {
  return del<{ deleted: boolean }>(`/tenants/staff/${id}`)
}
