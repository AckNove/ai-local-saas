import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'

// 路由级权限守卫：
// - 未登录 → 跳 /login
// - 传入 roles 且当前角色不在其中 → 展示「无权限」

interface Props {
  children: ReactNode
  roles?: string[]
}

export default function ProtectedRoute({ children, roles }: Props) {
  const { isAuthenticated, user } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (roles && user && !roles.includes(user.role)) {
    return (
      <div className="p-10 text-center text-gray-500">
        <div className="text-2xl mb-2">🚫 无访问权限</div>
        <div>当前角色无权访问该页面。</div>
      </div>
    )
  }

  return <>{children}</>
}
