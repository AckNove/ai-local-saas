import { useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth, roleLabel } from '../auth/AuthContext'
import { changePassword } from '../api/auth'

// 后台布局：左侧按角色显隐的菜单 + 顶部用户信息。

interface Menu {
  to: string
  label: string
  icon: string
  roles: string[] // 可见角色
}

const MENUS: Menu[] = [
  { to: '/merchants', label: '商户管理', icon: '🏢', roles: ['platform_operator'] },
  { to: '/staff', label: '员工管理', icon: '👥', roles: ['platform_operator', 'merchant_owner'] },
  { to: '/stores', label: '门店管理', icon: '🏪', roles: ['platform_operator', 'merchant_owner', 'store_manager'] },
  { to: '/packages', label: '套餐管理', icon: '🍱', roles: ['platform_operator', 'merchant_owner', 'store_manager'] },
  { to: '/orders', label: '订单与核销', icon: '📦', roles: ['platform_operator', 'merchant_owner', 'store_manager', 'verifier'] },
  { to: '/reservations', label: '预约管理', icon: '📅', roles: ['platform_operator', 'merchant_owner', 'store_manager', 'verifier'] },
  { to: '/channels', label: '视频号挂载', icon: '🎬', roles: ['platform_operator', 'merchant_owner', 'store_manager'] },
  { to: '/dashboard', label: '数据看板', icon: '📊', roles: ['platform_operator', 'merchant_owner', 'store_manager', 'verifier'] },
]

export default function AdminLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [pwdOpen, setPwdOpen] = useState(false)
  const [oldPwd, setOldPwd] = useState('')
  const [newPwd, setNewPwd] = useState('')
  const [confirmPwd, setConfirmPwd] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const visibleMenus = MENUS.filter((m) => user && m.roles.includes(user.role))

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const handleChangePwd = async () => {
    setError('')
    if (!oldPwd || !newPwd) {
      setError('请填写原密码和新密码')
      return
    }
    if (newPwd.length < 6) {
      setError('新密码至少 6 位')
      return
    }
    if (newPwd !== confirmPwd) {
      setError('两次输入的新密码不一致')
      return
    }
    setSubmitting(true)
    try {
      await changePassword(oldPwd, newPwd)
      setPwdOpen(false)
      setOldPwd('')
      setNewPwd('')
      setConfirmPwd('')
      alert('密码修改成功')
    } catch (err) {
      setError(err instanceof Error ? err.message : '修改失败')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* 侧边栏 */}
      <aside className="w-56 bg-gray-900 text-gray-200 flex flex-col">
        <div className="px-4 py-4 text-lg font-semibold text-white border-b border-gray-700">
          视频号团购 SaaS
        </div>
        <nav className="flex-1 py-2">
          {visibleMenus.map((m) => (
            <NavLink
              key={m.to}
              to={m.to}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-3 text-sm hover:bg-gray-800 ${
                  isActive ? 'bg-gray-800 text-white border-l-2 border-brand' : 'text-gray-300'
                }`
              }
            >
              <span>{m.icon}</span>
              <span>{m.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* 主区 */}
      <div className="flex-1 flex flex-col">
        <header className="h-14 bg-white border-b flex items-center justify-between px-6">
          <div className="text-sm text-gray-500">管理后台</div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-gray-700">
              {user?.name || user?.username}（{roleLabel(user?.role)}）
            </span>
            <button className="btn-ghost" onClick={() => setPwdOpen(true)}>
              修改密码
            </button>
            <button className="btn-ghost" onClick={handleLogout}>
              退出登录
            </button>
          </div>
        </header>
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>

      {pwdOpen && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-10">
          <div className="card w-[400px]">
            <div className="text-lg font-semibold mb-3">修改密码</div>
            <label className="label">原密码</label>
            <input
              className="input mb-3"
              type="password"
              value={oldPwd}
              onChange={(e) => setOldPwd(e.target.value)}
            />
            <label className="label">新密码（至少 6 位）</label>
            <input
              className="input mb-3"
              type="password"
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
            />
            <label className="label">确认新密码</label>
            <input
              className="input mb-3"
              type="password"
              value={confirmPwd}
              onChange={(e) => setConfirmPwd(e.target.value)}
            />
            {error && <div className="text-red-500 text-sm mb-3">{error}</div>}
            <div className="flex justify-end gap-2 mt-2">
              <button className="btn-ghost" onClick={() => setPwdOpen(false)}>
                取消
              </button>
              <button className="btn-primary" onClick={handleChangePwd} disabled={submitting}>
                {submitting ? '提交中…' : '确认修改'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
