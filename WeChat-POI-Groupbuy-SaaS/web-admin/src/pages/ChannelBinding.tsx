import { useEffect, useState } from 'react'
import {
  createVideoBinding,
  deleteVideoBinding,
  listVideoBindings,
} from '../api/dashboard'
import { listStores } from '../api/stores'
import { ApiError } from '../api/client'
import type { Store, VideoBinding, VideoBindingInput } from '../types'

// 视频号 POI/团购挂载管理（T08）。
export default function ChannelBinding() {
  const [bindings, setBindings] = useState<VideoBinding[]>([])
  const [stores, setStores] = useState<Store[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState<VideoBindingInput>({ store_id: 0, video_account_id: '', poi_id: '' })

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [bs, ss] = await Promise.all([
        listVideoBindings(),
        listStores({ page: 1, page_size: 100 }),
      ])
      setBindings(bs.list)
      setStores(ss.list)
      if (ss.list.length && form.store_id === 0) {
        setForm((f) => ({ ...f, store_id: ss.list[0].id }))
      }
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

  const handleCreate = async () => {
    setError('')
    if (!form.store_id || !form.video_account_id) {
      setError('请选择门店并填写视频号账号 ID')
      return
    }
    try {
      await createVideoBinding(form)
      setForm({ store_id: stores[0]?.id ?? 0, video_account_id: '', poi_id: '' })
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '绑定失败')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await deleteVideoBinding(id)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '解绑失败')
    }
  }

  const storeName = (id: number) => stores.find((s) => s.id === id)?.name ?? `#${id}`

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">视频号挂载与内容引流</h2>

      <div className="card mb-4">
        <div className="text-sm font-medium mb-3">新建挂载</div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
          <div>
            <label className="label">门店</label>
            <select
              className="input"
              value={form.store_id}
              onChange={(e) => setForm({ ...form, store_id: Number(e.target.value) })}
            >
              {stores.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">视频号账号 ID</label>
            <input
              className="input"
              value={form.video_account_id}
              onChange={(e) => setForm({ ...form, video_account_id: e.target.value })}
              placeholder="如 vlog_abc123"
            />
          </div>
          <div>
            <label className="label">POI ID（可选）</label>
            <input
              className="input"
              value={form.poi_id ?? ''}
              onChange={(e) => setForm({ ...form, poi_id: e.target.value })}
              placeholder="留空则按门店 POI"
            />
          </div>
          <div>
            <button className="btn-primary w-full" onClick={handleCreate}>
              + 绑定
            </button>
          </div>
        </div>
        {error && <div className="text-red-500 text-sm mt-3">{error}</div>}
      </div>

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>门店</th>
              <th>视频号账号</th>
              <th>POI</th>
              <th>团购链接</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {bindings.map((b) => (
              <tr key={b.id}>
                <td>{b.id}</td>
                <td>{storeName(b.store_id)}</td>
                <td>{b.video_account_id}</td>
                <td>{b.poi_name || b.poi_id || '-'}</td>
                <td className="max-w-[220px] truncate" title={b.groupbuy_link ?? ''}>
                  {b.groupbuy_link ? (
                    <a className="text-brand" href={b.groupbuy_link} target="_blank" rel="noreferrer">
                      {b.groupbuy_link}
                    </a>
                  ) : (
                    '-'
                  )}
                </td>
                <td>{b.status === 'active' ? '生效中' : b.status}</td>
                <td>
                  <button className="btn-danger" onClick={() => handleDelete(b.id)}>
                    解绑
                  </button>
                </td>
              </tr>
            ))}
            {!loading && bindings.length === 0 && (
              <tr>
                <td colSpan={7} className="text-center text-gray-400 py-6">
                  暂无挂载
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
