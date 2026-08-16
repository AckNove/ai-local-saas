import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { webLogin } from '../api/auth'
import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'

// Web 登录页（平台/商户/店长/核销员）。
export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const tokenOut = await webLogin(username.trim(), password)
      login(tokenOut)
      navigate('/orders', { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '登录失败，请检查网络')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="card w-96">
        <div className="text-xl font-semibold mb-1">视频号团购 SaaS</div>
        <div className="text-sm text-gray-400 mb-5">管理后台登录</div>

        <label className="label">账号</label>
        <input
          className="input mb-3"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="如 admin / merchant / manager / verifier"
          autoFocus
        />

        <label className="label">密码</label>
        <input
          className="input mb-3"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="密码"
        />

        {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

        <button className="btn-primary w-full" disabled={loading}>
          {loading ? '登录中…' : '登录'}
        </button>

        <div className="text-xs text-gray-400 mt-4 leading-relaxed">
          演示账号：<br />
          admin/admin123（平台）· merchant/merchant123（商户）<br />
          manager/manager123（店长）· verifier/verifier123（核销员）
        </div>
      </form>
    </div>
  )
}
