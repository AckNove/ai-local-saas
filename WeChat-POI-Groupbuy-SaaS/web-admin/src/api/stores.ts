import { get, post, patch } from './client'
import type { PageResult, Store, StoreInput } from '../types'

// 门店接口封装（含地图 POI 绑定）。

export function listStores(params?: {
  merchant_id?: number
  page?: number
  page_size?: number
}): Promise<PageResult<Store>> {
  return get<PageResult<Store>>('/tenants/stores', params)
}

export function createStore(body: StoreInput): Promise<Store> {
  return post<Store>('/tenants/stores', body)
}

export function updateStore(id: number, body: Partial<StoreInput>): Promise<Store> {
  return patch<Store>(`/tenants/stores/${id}`, body)
}

/** 绑定/解绑地图 POI：直接以 POI 字段 PATCH 门店（后端经 MapProvider 落库）。 */
export function bindPoi(
  id: number,
  poi: { poi_id?: string | null; poi_name?: string | null; lng?: number | null; lat?: number | null },
): Promise<Store> {
  return patch<Store>(`/tenants/stores/${id}`, poi)
}
