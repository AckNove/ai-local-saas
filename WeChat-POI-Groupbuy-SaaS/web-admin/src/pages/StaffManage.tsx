import { useEffect, useState } from 'react'
import { createStaff, deleteStaff, listStaff, updateStaff } from '../api/tenants'
import { listStores } from '../api/stores'
import { ApiError } from '../api/client'
import type { Staff, StaffInput, Store } from '../types'

const ROLE_TEXT: Record<string, string> = {
  store_manager: '店长',
  verifier: '核销员',
}

// 员工管理：核销员 / 店长账号分配（平台运营 / 商户主可用）。
export default function StaffManage() {
  const [staff, setStaff] = useState<Staff[]>([])
  const [stores, setStores] = useState<Store[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Staff | null>(null)
  const [form, setForm] = useState<StaffInput>({
    name: '',
    role: 'verifier',
    store_id: 0,
    username: '',
    password: '',
    phone: '',
  })

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [page, spage] = await Promise.all([
        listStaff({ page: 1, page_size: 100 }),
        listStores({ page: 1, page_size: 100 }),
      ])
      setStaff(page.list)
      setStores(spage.list)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const storeName = (id: number) => stores.find((s) => s.id === id)?.name ?? `#${id}`

  const openCreate = () => {
    setEditing(null)
    setForm({
      name: '',
      role: 'verifier',
      store_id: stores[0]?.id ?? 0,
      username: '',
      password: '',
      phone: '',
    })
    setShowModal(true)
  }

  const openEdit = (s: Staff) => {
    setEditing(s)
    setForm({
      name: s.name,
      role: (s.role as StaffInput['role']) ?? 'verifier',
      store_id: s.store_id,
      username: s.username ?? '',
      password: '',
      phone: s.phone ?? '',
    })
    setShowModal(true)
  }

  const save = async () => {
    setError('')
    if (!form.name.trim()) {
      setError('请填写姓名')
      return
    }
    if (!form.store_id) {
      setError('请选择所属门店')
      return
    }
    try {
      const payload: StaffInput = {
        name: form.name.trim(),
        role: form.role,
        store_id: form.store_id,
        username: form.username?.trim() || null,
        password: form.password || null,
        phone: form.phone?.trim() || null,
      }
      if (editing) await updateStaff(editing.id, payload)
      else await createStaff(payload)
      setShowModal(false)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '保存失败')
    }
  }

  const handleDelete = async (s: Staff) => {
    if (!window.confirm(`确定删除员工「${s.name}」吗？`)) return
    try {
      await deleteStaff(s.id)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '删除失败')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">员工管理</h2>
        <button className="btn-primary" onClick={openCreate}>
          + 新增员工
        </button>
      </div>

      {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>姓名</th>
              <th>角色</th>
              <th>所属门店</th>
              <th>登录名</th>
              <th>电话</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {staff.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{ROLE_TEXT[s.role] ?? s.role}</td>
                <td>{storeName(s.store_id)}</td>
                <td>{s.username || '-'}</td>
                <td>{s.phone || '-'}</td>
                <td>{s.is_active ? '在职' : '停用'}</td>
                <td className="whitespace-nowrap">
                  <button className="btn-ghost mr-2" onClick={() => openEdit(s)}>
                    编辑
                  </button>
                  <button className="btn-danger" onClick={() => handleDelete(s)}>
                    删除
                  </button>
                </td>
              </tr>
            ))}
            {!loading && staff.length === 0 && (
              <tr>
                <td colSpan={8} className="text-center text-gray-400 py-6">
                  暂无员工
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-10">
          <div className="card w-[440px] max-h-[90vh] overflow-auto">
            <div className="text-lg font-semibold mb-3">{editing ? '编辑员工' : '新增员工'}</div>

            <label className="label">姓名 *</label>
            <input
              className="input mb-3"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="如：小李"
            />

            <label className="label">角色 *</label>
            <select
              className="input mb-3"
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value as StaffInput['role'] })}
            >
              <option value="verifier">核销员</option>
              <option value="store_manager">店长</option>
            </select>

            <label className="label">所属门店 *</label>
            <select
              className="input mb-3"
              value={form.store_id}
              onChange={(e) => setForm({ ...form, store_id: Number(e.target.value) })}
            >
              {stores.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>

            <label className="label">登录名（可空）</label>
            <input
              className="input mb-3"
              value={form.username ?? ''}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              placeholder="用于 Web/小程序登录"
            />

            <label className="label">{editing ? '新密码（留空不修改）' : '初始密码'}</label>
            <input
              className="input mb-3"
              type="password"
              value={form.password ?? ''}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder={editing ? '留空保持原密码' : '如 123456'}
            />

            <label className="label">电话（可空）</label>
            <input
              className="input mb-3"
              value={form.phone ?? ''}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />

            {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

            <div className="flex justify-end gap-2 mt-2">
              <button className="btn-ghost" onClick={() => setShowModal(false)}>
                取消
              </button>
              <button className="btn-primary" onClick={save}>
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
