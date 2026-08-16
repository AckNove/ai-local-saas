import { useEffect, useState } from 'react'
import {
  createPackage,
  listPackages,
  offShelfPackage,
  publishPackage,
  updatePackage,
  uploadImage,
} from '../api/packages'
import { listStores } from '../api/stores'
import { ApiError } from '../api/client'
import type { Package, PackageInput, Store } from '../types'
import { formatMoney } from '../utils/format'

// 套餐管理：列表 / 上架下架 / 新建编辑（原价·团购价以「元」录入，提交转「分」）。
export default function PackageManage() {
  const [packages, setPackages] = useState<Package[]>([])
  const [stores, setStores] = useState<Store[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing] = useState<Package | null>(null)
  const [form, setForm] = useState<PackageInput>(blankForm())
  const [imageUrls, setImageUrls] = useState<string[]>([])
  const [keyword, setKeyword] = useState('')

  function blankForm(): PackageInput {
    return {
      name: '',
      description: '',
      original_price: 0,
      group_price: 0,
      stock: 0,
      valid_from: '',
      valid_to: '',
      images_json: '',
      store_ids: [],
    }
  }

  /** 解析 images_json 为图片 URL 列表（兼容 {"images":[...]} 与裸数组）。 */
  function parseImages(imagesJson: string | null | undefined): string[] {
    if (!imagesJson) return []
    try {
      const parsed = JSON.parse(imagesJson)
      if (Array.isArray(parsed)) return parsed.filter((x) => typeof x === 'string')
      if (parsed && Array.isArray(parsed.images)) return parsed.images.filter((x: unknown) => typeof x === 'string')
      return []
    } catch {
      return []
    }
  }

  /** 把图片 URL 列表序列化为后端 images_json 格式。 */
  function serializeImages(urls: string[]): string {
    const cleaned = urls.map((u) => u.trim()).filter(Boolean)
    return JSON.stringify({ images: cleaned })
  }

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const [page, spage] = await Promise.all([
        listPackages({ page: 1, page_size: 100, keyword: keyword.trim() || undefined }),
        listStores({ page: 1, page_size: 100 }),
      ])
      setPackages(page.list)
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

  useEffect(() => {
    const t = setTimeout(() => load(), 300) // 防抖
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keyword])

  const openCreate = () => {
    setEditing(null)
    setForm(blankForm())
    setImageUrls([])
    setShowModal(true)
  }

  const openEdit = (p: Package) => {
    setEditing(p)
    setForm({
      name: p.name,
      description: p.description ?? '',
      original_price: p.original_price / 100,
      group_price: p.group_price / 100,
      stock: p.stock,
      valid_from: p.valid_from ?? '',
      valid_to: p.valid_to ?? '',
      images_json: p.images_json ?? '',
      store_ids: p.store_ids,
    })
    setImageUrls(parseImages(p.images_json))
    setShowModal(true)
  }

  const save = async () => {
    setError('')
    try {
      const payload: PackageInput = {
        ...form,
        original_price: Math.round((form.original_price || 0) * 100),
        group_price: Math.round((form.group_price || 0) * 100),
        stock: form.stock ?? 0,
        store_ids: form.store_ids ?? [],
        images_json: serializeImages(imageUrls),
      }
      if (editing) await updatePackage(editing.id, payload)
      else await createPackage(payload)
      setShowModal(false)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '保存失败')
    }
  }

  const updateImageUrl = (idx: number, value: string) => {
    setImageUrls((prev) => prev.map((u, i) => (i === idx ? value : u)))
  }

  const addImageUrl = () => setImageUrls((prev) => [...prev, ''])

  const removeImageUrl = (idx: number) =>
    setImageUrls((prev) => prev.filter((_, i) => i !== idx))

  const handleUploadImage = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setError('')
    try {
      const url = await uploadImage(file)
      setImageUrls((prev) => [...prev, url])
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败')
    } finally {
      // 清空 input，允许重复选择同一文件
      e.target.value = ''
    }
  }

  const togglePublish = async (p: Package) => {
    try {
      if (p.status === 'published') await offShelfPackage(p.id)
      else await publishPackage(p.id)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '操作失败')
    }
  }

  const toggleStore = (id: number) => {
    const set = new Set(form.store_ids ?? [])
    if (set.has(id)) set.delete(id)
    else set.add(id)
    setForm({ ...form, store_ids: Array.from(set) })
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">套餐管理</h2>
        <div className="flex items-center gap-2">
          <input
            className="input w-56"
            placeholder="搜索套餐名称"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <button className="btn-primary" onClick={openCreate}>
            + 新建套餐
          </button>
        </div>
      </div>

      {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>原价</th>
              <th>团购价</th>
              <th>库存</th>
              <th>已售</th>
              <th>适用门店</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {packages.map((p) => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>{p.name}</td>
                <td>{formatMoney(p.original_price)}</td>
                <td className="text-brand font-medium">{formatMoney(p.group_price)}</td>
                <td>{p.stock}</td>
                <td>{p.sold_count}</td>
                <td>{p.store_ids.length} 家</td>
                <td>
                  {p.status === 'published' ? (
                    <span className="text-brand">已上架</span>
                  ) : (
                    <span className="text-gray-400">未上架</span>
                  )}
                </td>
                <td className="whitespace-nowrap">
                  <button className="btn-ghost mr-2" onClick={() => openEdit(p)}>
                    编辑
                  </button>
                  <button className="btn-primary" onClick={() => togglePublish(p)}>
                    {p.status === 'published' ? '下架' : '上架'}
                  </button>
                </td>
              </tr>
            ))}
            {!loading && packages.length === 0 && (
              <tr>
                <td colSpan={9} className="text-center text-gray-400 py-6">
                  暂无套餐
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-10">
          <div className="card w-[520px] max-h-[90vh] overflow-auto">
            <div className="text-lg font-semibold mb-3">
              {editing ? '编辑套餐' : '新建套餐'}
            </div>

            <label className="label">套餐名称</label>
            <input
              className="input mb-3"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />

            <label className="label">描述</label>
            <textarea
              className="input mb-3"
              rows={2}
              value={form.description ?? ''}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">原价（元）</label>
                <input
                  className="input mb-3"
                  type="number"
                  value={form.original_price}
                  onChange={(e) => setForm({ ...form, original_price: Number(e.target.value) })}
                />
              </div>
              <div>
                <label className="label">团购价（元）</label>
                <input
                  className="input mb-3"
                  type="number"
                  value={form.group_price}
                  onChange={(e) => setForm({ ...form, group_price: Number(e.target.value) })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">库存</label>
                <input
                  className="input mb-3"
                  type="number"
                  value={form.stock ?? 0}
                  onChange={(e) => setForm({ ...form, stock: Number(e.target.value) })}
                />
              </div>
              <div>
                <label className="label">套餐图片（本地上传或填 URL，可多张）</label>
                <div className="space-y-2 mb-2">
                  {imageUrls.map((url, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input
                        className="input flex-1"
                        value={url}
                        onChange={(e) => updateImageUrl(idx, e.target.value)}
                        placeholder={`图片 ${idx + 1} 地址，如 https://...`}
                      />
                      {url.trim() && (
                        <img
                          src={url.trim()}
                          alt="预览"
                          className="w-10 h-10 object-cover rounded border"
                          onError={(e) => ((e.target as HTMLImageElement).style.opacity = '0.3')}
                          onLoad={(e) => ((e.target as HTMLImageElement).style.opacity = '1')}
                        />
                      )}
                      <button
                        className="btn-danger px-2 py-1 text-xs"
                        onClick={() => removeImageUrl(idx)}
                      >
                        删
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  <label className="btn-primary text-sm px-3 py-1.5 cursor-pointer inline-block">
                    上传图片
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={handleUploadImage}
                    />
                  </label>
                  <button className="btn-ghost text-sm" onClick={addImageUrl}>
                    + 填 URL
                  </button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">生效开始（ISO，可选）</label>
                <input
                  className="input mb-3"
                  value={form.valid_from ?? ''}
                  onChange={(e) => setForm({ ...form, valid_from: e.target.value })}
                />
              </div>
              <div>
                <label className="label">生效结束（ISO，可选）</label>
                <input
                  className="input mb-3"
                  value={form.valid_to ?? ''}
                  onChange={(e) => setForm({ ...form, valid_to: e.target.value })}
                />
              </div>
            </div>

            <label className="label">适用门店</label>
            <div className="flex flex-wrap gap-2 mb-3 max-h-32 overflow-auto">
              {stores.map((s) => {
                const checked = (form.store_ids ?? []).includes(s.id)
                return (
                  <label
                    key={s.id}
                    className={`text-sm px-2 py-1 rounded border cursor-pointer ${
                      checked ? 'border-brand text-brand bg-green-50' : 'border-gray-300 text-gray-600'
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="mr-1"
                      checked={checked}
                      onChange={() => toggleStore(s.id)}
                    />
                    {s.name}
                  </label>
                )
              })}
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
