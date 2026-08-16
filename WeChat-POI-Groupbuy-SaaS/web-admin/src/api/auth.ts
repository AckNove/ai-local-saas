import { post } from './client'
import type { TokenOut } from '../types'

// 认证接口封装

/** Web/员工登录（平台/商户/店长/核销员）。 */
export function webLogin(username: string, password: string): Promise<TokenOut> {
  return post<TokenOut>('/auth/web-login', { username, password })
}

/** 修改当前登录账号密码。 */
export function changePassword(old_password: string, new_password: string): Promise<{ changed: boolean }> {
  return post<{ changed: boolean }>('/auth/change-password', { old_password, new_password })
}
