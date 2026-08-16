import { get, patch } from './client'
import type { PageResult, Order } from '../types'

// 订单接口封装。

export function listOrders(params?: {
  status?: string
  keyword?: string
  store_id?: number
  page?: number
  page_size?: number
}): Promise<PageResult<Order>> {
  return get<PageResult<Order>>('/orders', params)
}

export function getOrder(orderNo: string): Promise<Order> {
  return get<Order>(`/orders/${orderNo}`)
}

/** 商家/核销员更新自提备餐状态：preparing / ready / picked_up。 */
export function updatePickup(orderNo: string, status: string): Promise<Order> {
  return patch<Order>(`/orders/${orderNo}/pickup`, { status })
}
