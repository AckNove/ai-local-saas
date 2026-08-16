import { useEffect, useState } from 'react'
import { createMerchant, deleteMerchant, listMerchants, updateMerchant } from '../api/tenants'
import { listStores } from '../api/stores'
import { ApiError } from '../api/client'
import type { Merchant, Store } from '../types'

// 商户管理：列表 / 新增 / 编辑 / 停用启用 / 软删除（平台运营专属）。
export default function MerchantManage() {
  const [merchants, setMerchants] = useState<Merchant[]>([])
  const [stores, setStores] = useState<Store[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Merchant | null>(null)
  const [form, setForm] = useState({ name: '', logo_url: '', contact_phone: '', merchant_code: '' })

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [page, spage] = await Promise.all([
        listMerchants({ page: 1, page_size: 100 }),
        listStores({ page: 1, page_size: 100 }),
      ])
      setMerchants(page.list)
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

  const storeCount = (merchantId: number) =>
    stores.filter((s) => s.merchant_id === merchantId).length

  const openCreate = () => {
    setEditing(null)
    setForm({ name: '', logo_url: '', contact_phone: '', merchant_code: '' })
    setShowModal(true)
  }

  const openEdit = (m: Merchant) => {
    setEditing(m)
    setForm({
      name: m.name,
      logo_url: m.logo_url ?? '',
      contact_phone: m.contact_phone ?? '',
      merchant_code: m.merchant_code ?? '',
    })
    setShowModal(true)
  }

  const save = async () => {
    setError('')
    if (!form.name.trim()) {
      setError('请填写商户名称')
      return
    }
    try {
      const payload = {
        name: form.name.trim(),
        logo_url: form.logo_url.trim() || null,
        contact_phone: form.contact_phone.trim() || null,
        merchant_code: form.merchant_code.trim() || null,
      }
      if (editing) await updateMerchant(editing.id, payload)
      else await createMerchant(payload)
      setShowModal(false)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '保存失败')
    }
  }

  const toggleStatus = async (m: Merchant) => {
    try {
      await updateMerchant(m.id, { status: m.status === 'disabled' ? 'active' : 'disabled' })
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '操作失败')
    }
  }

  const handleDelete = async (m: Merchant) => {
    if (!window.confirm(`确定删除商户「${m.name}」吗？（软删除，门店与套餐保留）`)) return
    try {
      await deleteMerchant(m.id)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '删除失败')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">商户管理</h2>
        <button className="btn-primary" onClick={openCreate}>
          + 新增商户
        </button>
      </div>

      {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>商家标识</th>
              <th>Logo</th>
              <th>联系电话</th>
              <th>门店数</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {merchants.map((m) => (
              <tr key={m.id}>
                <td>{m.id}</td>
                <td className="font-medium">{m.name}</td>
                <td className="font-mono text-xs">
                  {m.merchant_code ? (
                    <span className="text-brand">{m.merchant_code}</span>
                  ) : (
                    <span className="text-gray-400">未设置</span>
                  )}
                </td>
                <td>
                  {m.logo_url ? (
                    <img
                      src={m.logo_url}
                      alt="logo"
                      className="w-8 h-8 object-cover rounded"
                      onError={(e) => ((e.target as HTMLImageElement).style.display = 'none')}
                    />
                  ) : (
                    '-'
                  )}
                </td>
                <td>{m.contact_phone || '-'}</td>
                <td>{storeCount(m.id)}</td>
                <td>
                  {m.status === 'disabled' ? (
                    <span className="text-gray-400">已停用</span>
                  ) : (
                    <span className="text-brand">正常</span>
                  )}
                </td>
                <td className="whitespace-nowrap">
                  <button className="btn-ghost mr-2" onClick={() => openEdit(m)}>
                    编辑
                  </button>
                  <button className="btn-ghost mr-2" onClick={() => toggleStatus(m)}>
                    {m.status === 'disabled' ? '启用' : '停用'}
                  </button>
                  <button className="btn-danger" onClick={() => handleDelete(m)}>
                    删除
                  </button>
                </td>
              </tr>
            ))}
            {!loading && merchants.length === 0 && (
              <tr>
                <td colSpan={8} className="text-center text-gray-400 py-6">
                  暂无商户
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-10">
          <div className="card w-[440px]">
            <div className="text-lg font-semibold mb-3">{editing ? '编辑商户' : '新增商户'}</div>

            <label className="label">商户名称 *</label>
            <input
              className="input mb-3"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="如：某某餐饮集团"
            />

            <label className="label">Logo URL（可选）</label>
            <input
              className="input mb-3"
              value={form.logo_url}
              onChange={(e) => setForm({ ...form, logo_url: e.target.value })}
              placeholder="https://..."
            />

            <label className="label">联系电话（可选）</label>
            <input
              className="input mb-3"
              value={form.contact_phone}
              onChange={(e) => setForm({ ...form, contact_phone: e.target.value })}
              placeholder="13800000000"
            />

            <label className="label">商家标识（小程序用，唯一）</label>
            <input
              className="input mb-3"
              value={form.merchant_code}
              onChange={(e) => setForm({ ...form, merchant_code: e.target.value })}
              placeholder="如：shop_abc，填进小程序 config.js 的 MERCHANT_CODE"
            />
            <p className="text-xs text-gray-400 mb-3">
              填了后，小程序 config.js 里 MERCHANT_CODE 填这个值，小程序就会自动加载该商家的品牌与套餐。
            </p>

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
