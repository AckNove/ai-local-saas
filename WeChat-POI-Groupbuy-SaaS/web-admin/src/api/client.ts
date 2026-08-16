import axios from 'axios'

// 统一 API 客户端：
// - baseURL 取自 VITE_API_BASE（默认后端 :8000/api/v1）
// - 请求拦截：注入 Bearer token
// - 响应拦截：统一 {code,message,data} 解析；非 0 抛 ApiError；401 跳登录
// - 提供 get/post/patch/del 泛型封装，直接返回 data 字段

export const API_BASE =
  import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api/v1'

const TOKEN_KEY = 'wp_token'

export class ApiError extends Error {
  code: number
  constructor(code: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.code = code
  }
}

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (resp) => {
    const body = resp.data
    if (body && typeof body === 'object' && 'code' in body) {
      if (body.code === 0) {
        return resp // 成功，data 字段由泛型封装取出
      }
      throw new ApiError(body.code ?? -1, body.message || '请求失败')
    }
    return resp
  },
  (error) => {
    const status = error.response?.status
    const body = error.response?.data
    if (status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem('wp_user')
      if (location.pathname !== '/login') {
        location.href = '/login'
      }
    }
    const message = body?.message || error.message || '网络错误'
    return Promise.reject(new ApiError(body?.code ?? status ?? -1, message))
  },
)

/** GET，返回 data 字段（已解包 {code,message,data}）。 */
export async function get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const r = await client.get(url, { params })
  return r.data.data as T
}

/** POST，返回 data 字段。 */
export async function post<T>(url: string, body?: unknown): Promise<T> {
  const r = await client.post(url, body)
  return r.data.data as T
}

/** PATCH，返回 data 字段。 */
export async function patch<T>(url: string, body?: unknown): Promise<T> {
  const r = await client.patch(url, body)
  return r.data.data as T
}

/** DELETE，返回 data 字段。 */
export async function del<T>(url: string): Promise<T> {
  const r = await client.delete(url)
  return r.data.data as T
}

export default client
