import { useEffect, useState } from 'react'
import { bindPoi, createStore, listStores, updateStore } from '../api/stores'
import { listMerchants } from '../api/tenants'
import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import type { Merchant, Store, StoreInput } from '../types'

// 门店管理：列表 / 新增 / 编辑 / 绑定·解绑地图 POI。
export default function StoreManage() {
  const { user } = useAuth()
  const isPlatform = user?.role === 'platform_operator'
  const [stores, setStores] = useState<Store[]>([])
  const [merchants, setMerchants] = useState<Merchant[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Store | null>(null)
  const [form, setForm] = useState<StoreInput>(blankForm())

  function blankForm(): StoreInput {
    return {
      name: '',
      merchant_id: null,
      address: '',
      phone: '',
      business_hours: '',
      poi_id: '',
      poi_name: '',
      lng: null,
      lat: null,
    }
  }

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [page, mpage] = await Promise.all([
        listStores({ page: 1, page_size: 100 }),
        listMerchants({ page: 1, page_size: 100 }),
      ])
      setStores(page.list)
      setMerchants(mpage.list)
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

  const openCreate = () => {
    setEditing(null)
    setForm({ ...blankForm(), merchant_id: isPlatform ? (merchants[0]?.id ?? null) : null })
    setShowModal(true)
  }

  const openEdit = (s: Store) => {
    setEditing(s)
    setForm({
      name: s.name,
      merchant_id: s.merchant_id,
      address: s.address ?? '',
      phone: s.phone ?? '',
      business_hours: s.business_hours ?? '',
      poi_id: s.poi_id ?? '',
      poi_name: s.poi_name ?? '',
      lng: s.lng ?? null,
      lat: s.lat ?? null,
    })
    setShowModal(true)
  }

  const save = async () => {
    setError('')
    try {
      const payload: StoreInput = {
        ...form,
        lng: form.lng === null || Number.isNaN(form.lng) ? null : form.lng,
        lat: form.lat === null || Number.isNaN(form.lat) ? null : form.lat,
      }
      if (editing) await updateStore(editing.id, payload)
      else await createStore(payload)
      setShowModal(false)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '保存失败')
    }
  }

  const handleUnbindPoi = async (s: Store) => {
    try {
      await bindPoi(s.id, { poi_id: null, poi_name: null, lng: null, lat: null })
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '解绑失败')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">门店管理</h2>
        <button className="btn-primary" onClick={openCreate}>
          + 新增门店
        </button>
      </div>

      {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>地址</th>
              <th>电话</th>
              <th>营业时间</th>
              <th>地图 POI</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {stores.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.name}</td>
                <td>{s.address || '-'}</td>
                <td>{s.phone || '-'}</td>
                <td>{s.business_hours || '-'}</td>
                <td>
                  {s.poi_name ? (
                    <span className="text-brand">
                      📍 {s.poi_name}
                      {s.poi_id ? `（${s.poi_id}）` : ''}
                    </span>
                  ) : (
                    <span className="text-gray-400">未绑定</span>
                  )}
                </td>
                <td className="whitespace-nowrap">
                  <button className="btn-ghost mr-2" onClick={() => openEdit(s)}>
                    编辑
                  </button>
                  {s.poi_name && (
                    <button className="btn-danger" onClick={() => handleUnbindPoi(s)}>
                      解绑POI
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {!loading && stores.length === 0 && (
              <tr>
                <td colSpan={7} className="text-center text-gray-400 py-6">
                  暂无门店
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-10">
          <div className="card w-[480px] max-h-[90vh] overflow-auto">
            <div className="text-lg font-semibold mb-3">
              {editing ? '编辑门店' : '新增门店'}
            </div>

            <label className="label">门店名称</label>
            <input
              className="input mb-3"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />

            {isPlatform && (
              <>
                <label className="label">所属商户 *</label>
                <select
                  className="input mb-3"
                  value={form.merchant_id ?? ''}
                  onChange={(e) => setForm({ ...form, merchant_id: Number(e.target.value) || null })}
                >
                  {merchants.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </>
            )}

            <label className="label">地址</label>
            <input
              className="input mb-3"
              value={form.address ?? ''}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
            />

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">电话</label>
                <input
                  className="input mb-3"
                  value={form.phone ?? ''}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                />
              </div>
              <div>
                <label className="label">营业时间</label>
                <input
                  className="input mb-3"
                  value={form.business_hours ?? ''}
                  onChange={(e) => setForm({ ...form, business_hours: e.target.value })}
                />
              </div>
            </div>

            <div className="border-t pt-3 mt-1">
              <div className="text-sm text-gray-500 mb-2">地图 POI（绑定后可在视频号挂载）</div>
              <label className="label">POI 名称</label>
              <input
                className="input mb-3"
                value={form.poi_name ?? ''}
                onChange={(e) => setForm({ ...form, poi_name: e.target.value })}
                placeholder="如：海底捞(朝阳店)"
              />
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label">POI ID</label>
                  <input
                    className="input mb-3"
                    value={form.poi_id ?? ''}
                    onChange={(e) => setForm({ ...form, poi_id: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">经度 lng</label>
                  <input
                    className="input mb-3"
                    value={form.lng ?? ''}
                    onChange={(e) =>
                      setForm({ ...form, lng: e.target.value === '' ? null : Number(e.target.value) })
                    }
                  />
                </div>
              </div>
              <label className="label">纬度 lat</label>
              <input
                className="input mb-3"
                value={form.lat ?? ''}
                onChange={(e) =>
                  setForm({ ...form, lat: e.target.value === '' ? null : Number(e.target.value) })
                }
              />
            </div>

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
