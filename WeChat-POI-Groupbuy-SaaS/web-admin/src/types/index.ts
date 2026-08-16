// 共享类型定义，与后端 Schema 对齐（金额一律为「分」整数）。

/** 登录用户输出（见后端 common.UserOut）。 */
export interface UserOut {
  id: number
  typ: 'platform' | 'merchant' | 'staff' | 'consumer'
  role: 'platform_operator' | 'merchant_owner' | 'store_manager' | 'verifier' | 'consumer'
  merchant_id?: number | null
  store_id?: number | null
  username?: string | null
  name?: string | null
}

/** 登录令牌输出（见后端 common.TokenOut）。 */
export interface TokenOut {
  token: string
  token_type: string
  user: UserOut
}

/** 统一分页返回（见后端 responses.paginate）。 */
export interface PageResult<T> {
  list: T[]
  total: number
  page: number
  page_size: number
}

// ---------------- 租户 / 门店 / 员工 ----------------
export interface Merchant {
  id: number
  name: string
  logo_url?: string | null
  contact_phone?: string | null
  merchant_code?: string | null
  status: string
  created_at?: string | null
}

export interface Store {
  id: number
  merchant_id: number
  name: string
  address?: string | null
  phone?: string | null
  business_hours?: string | null
  poi_id?: string | null
  poi_name?: string | null
  lng?: number | null
  lat?: number | null
  created_at?: string | null
}

export interface StoreInput {
  name: string
  merchant_id?: number | null
  address?: string | null
  phone?: string | null
  business_hours?: string | null
  poi_id?: string | null
  poi_name?: string | null
  lng?: number | null
  lat?: number | null
}

export interface Staff {
  id: number
  merchant_id: number
  store_id: number
  name: string
  role: string
  username?: string | null
  phone?: string | null
  openid?: string | null
  is_active: boolean
  created_at?: string | null
}

export interface StaffInput {
  name: string
  role: 'store_manager' | 'verifier'
  store_id: number
  username?: string | null
  password?: string | null
  phone?: string | null
  openid?: string | null
}

// ---------------- 套餐 ----------------
export interface Package {
  id: number
  merchant_id: number
  name: string
  description?: string | null
  original_price: number
  group_price: number
  stock: number
  sold_count: number
  valid_from?: string | null
  valid_to?: string | null
  status: string
  images_json?: string | null
  store_ids: number[]
  created_at?: string | null
}

export interface PackageInput {
  name: string
  description?: string | null
  original_price: number
  group_price: number
  stock?: number
  valid_from?: string | null
  valid_to?: string | null
  images_json?: string | null
  store_ids?: number[]
}

// ---------------- 订单 / 核销 ----------------
export interface VerificationCode {
  id: number
  code: string
  status: string
  expires_at?: string | null
}

export interface Order {
  id: number
  order_no: string
  consumer_id: number
  merchant_id: number
  store_id: number
  package_id: number
  quantity: number
  unit_price: number
  total_amount: number
  commission_amount: number
  status: string
  fulfillment_type: 'dine_in' | 'self_pickup' | 'reservation'
  pickup_status?: string | null
  source: string
  channel_binding_id?: number | null
  paid_at?: string | null
  expires_at?: string | null
  phone?: string | null
  created_at?: string | null
  verification_codes?: VerificationCode[]
}

// ---------------- 履约：预约 / 视频号 ----------------
export interface Reservation {
  id: number
  merchant_id: number
  store_id: number
  consumer_id: number
  order_id?: number | null
  reserve_date: string
  time_slot: string
  party_size: number
  table_no?: string | null
  area?: string | null
  status: string
  remark?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export interface VideoBinding {
  id: number
  merchant_id: number
  store_id: number
  video_account_id: string
  poi_id?: string | null
  poi_name?: string | null
  groupbuy_link?: string | null
  status: string
  created_at?: string | null
}

export interface VideoBindingInput {
  store_id: number
  video_account_id: string
  poi_id?: string | null
}

// ---------------- 数据看板指标 ----------------
export interface Metrics {
  sales_volume: number
  gmv: number
  paid_orders: number
  verified_count: number
  verify_rate: number
  self_pickup_rate: number
  video_channel_rate: number
  reservation_total: number
  reservation_rate: number
}
