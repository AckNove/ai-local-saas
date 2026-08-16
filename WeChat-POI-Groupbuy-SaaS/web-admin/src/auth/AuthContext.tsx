import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { TokenOut, UserOut } from '../types'

// 认证上下文：管理 JWT 存储、当前用户、角色解析。

interface AuthState {
  user: UserOut | null
  token: string | null
  isAuthenticated: boolean
  login: (t: TokenOut) => void
  logout: () => void
}

const AuthContext = createContext<AuthState | undefined>(undefined)

const TOKEN_KEY = 'wp_token'
const USER_KEY = 'wp_user'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_KEY),
  )
  const [user, setUser] = useState<UserOut | null>(() => {
    const raw = localStorage.getItem(USER_KEY)
    try {
      return raw ? (JSON.parse(raw) as UserOut) : null
    } catch {
      return null
    }
  })

  useEffect(() => {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  }, [token])

  useEffect(() => {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
    else localStorage.removeItem(USER_KEY)
  }, [user])

  const value = useMemo<AuthState>(
    () => ({
      user,
      token,
      isAuthenticated: !!token && !!user,
      login: (t: TokenOut) => {
        setToken(t.token)
        setUser(t.user)
      },
      logout: () => {
        setToken(null)
        setUser(null)
      },
    }),
    [user, token],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth 必须在 AuthProvider 内使用')
  return ctx
}

/** 角色 → 中文名。 */
export function roleLabel(role?: string | null): string {
  switch (role) {
    case 'platform_operator':
      return '平台运营'
    case 'merchant_owner':
      return '商户主账号'
    case 'store_manager':
      return '店长'
    case 'verifier':
      return '核销员'
    case 'consumer':
      return '消费者'
    default:
      return '未知'
  }
}
