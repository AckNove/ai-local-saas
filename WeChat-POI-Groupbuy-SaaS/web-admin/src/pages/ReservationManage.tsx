import { useEffect, useState } from 'react'
import { listReservations, updateReservation } from '../api/dashboard'
import { ApiError } from '../api/client'
import type { Reservation } from '../types'
import { formatTime } from '../utils/format'

const STATUS_TEXT: Record<string, string> = {
  pending: '待确认',
  confirmed: '已确认',
  arrived: '已到店',
  cancelled: '已取消',
  released: '已释放',
}

const STATUS_COLOR: Record<string, string> = {
  pending: 'text-amber-600',
  confirmed: 'text-brand',
  arrived: 'text-blue-600',
  cancelled: 'text-gray-400',
  released: 'text-gray-400',
}

// 预约订座管理（T07）。
export default function ReservationManage() {
  const [list, setList] = useState<Reservation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await listReservations({ page: 1, page_size: 100 })
      setList(res.list)
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

  const act = async (r: Reservation, status: string) => {
    try {
      await updateReservation(r.id, status)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '操作失败')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">预约订座管理</h2>
        <button className="btn-ghost" onClick={load}>
          刷新
        </button>
      </div>

      {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>门店ID</th>
              <th>日期</th>
              <th>时段</th>
              <th>人数</th>
              <th>状态</th>
              <th>备注</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {list.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.store_id}</td>
                <td>{r.reserve_date}</td>
                <td>{r.time_slot}</td>
                <td>{r.party_size}</td>
                <td className={STATUS_COLOR[r.status] ?? ''}>{STATUS_TEXT[r.status] ?? r.status}</td>
                <td>{r.remark || '-'}</td>
                <td>{formatTime(r.created_at)}</td>
                <td className="whitespace-nowrap">
                  {r.status === 'pending' && (
                    <button className="btn-primary mr-2" onClick={() => act(r, 'confirmed')}>
                      确认
                    </button>
                  )}
                  {(r.status === 'pending' || r.status === 'confirmed') && (
                    <button className="btn-ghost mr-2" onClick={() => act(r, 'arrived')}>
                      到店
                    </button>
                  )}
                  {(r.status === 'pending' || r.status === 'confirmed') && (
                    <button className="btn-danger" onClick={() => act(r, 'cancelled')}>
                      取消
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {!loading && list.length === 0 && (
              <tr>
                <td colSpan={9} className="text-center text-gray-400 py-6">
                  暂无预约
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
