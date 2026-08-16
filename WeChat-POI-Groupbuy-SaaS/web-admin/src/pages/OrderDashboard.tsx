import { useEffect, useState } from 'react'
import { listOrders, updatePickup } from '../api/orders'
import { getMetrics } from '../api/dashboard'
import { ApiError } from '../api/client'
import type { Metrics, Order } from '../types'
import { formatMoney, formatTime, todayStr } from '../utils/format'
import StatCard from '../components/StatCard'

const STATUS_TEXT: Record<string, string> = {
  pending_payment: '待支付',
  paid: '已支付',
  fulfilled: '已完成',
  refunded: '已退款',
  closed: '已关闭',
  cancelled: '已取消',
}

const FULFILL_TEXT: Record<string, string> = {
  dine_in: '堂食',
  self_pickup: '到店自提',
  reservation: '预约订座',
}

const PICKUP_TEXT: Record<string, string> = {
  preparing: '备餐中',
  ready: '待取',
  picked_up: '已取',
}

// 订单与核销看板。
export default function OrderDashboard() {
  const [orders, setOrders] = useState<Order[]>([])
  const [total, setTotal] = useState(0)
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [status, setStatus] = useState('')
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadOrders = async () => {
    setLoading(true)
    setError('')
    try {
      const page = await listOrders({
        status: status || undefined,
        keyword: keyword.trim() || undefined,
        page: 1,
        page_size: 50,
      })
      setOrders(page.list)
      setTotal(page.total)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const loadMetrics = async () => {
    try {
      const today = todayStr()
      const m = await getMetrics({ date_from: today, date_to: today })
      setMetrics(m)
    } catch {
      /* 看板指标非阻断 */
    }
  }

  useEffect(() => {
    loadOrders()
    loadMetrics()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    loadOrders()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, keyword])

  const handlePickup = async (o: Order, next: string) => {
    try {
      await updatePickup(o.order_no, next)
      await loadOrders()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '更新失败')
    }
  }

  const canPickup = (o: Order) =>
    o.fulfillment_type === 'self_pickup' && (o.status === 'paid' || o.status === 'fulfilled')
  const nextPickup = (o: Order) =>
    o.pickup_status === 'preparing' ? 'ready' : o.pickup_status === 'ready' ? 'picked_up' : 'ready'

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">订单与核销看板</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
        <StatCard
          title="今日 GMV"
          value={metrics ? formatMoney(metrics.gmv) : '—'}
          hint="已支付+已完成订单金额"
        />
        <StatCard
          title="今日核销率"
          value={metrics ? `${(metrics.verify_rate * 100).toFixed(1)}%` : '—'}
          hint="已核销/需核销"
          accent="#07c160"
        />
        <StatCard title="今日支付订单" value={metrics ? String(metrics.paid_orders) : '—'} />
        <StatCard title="今日已核销" value={metrics ? String(metrics.verified_count) : '—'} />
      </div>

      <div className="flex items-center gap-3 mb-3 flex-wrap">
        <span className="text-sm text-gray-500">状态筛选</span>
        <select className="input w-40" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">全部</option>
          <option value="pending_payment">待支付</option>
          <option value="paid">已支付</option>
          <option value="fulfilled">已完成</option>
          <option value="refunded">已退款</option>
        </select>
        <input
          className="input w-56"
          placeholder="搜索订单号 / 手机号"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
        />
        <span className="text-sm text-gray-400">共 {total} 单</span>
      </div>

      {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

      <div className="card overflow-x-auto">
        <table className="table">
          <thead>
            <tr>
              <th>订单号</th>
              <th>套餐ID</th>
              <th>门店ID</th>
              <th>数量</th>
              <th>金额</th>
              <th>履约</th>
              <th>状态</th>
              <th>自提</th>
              <th>下单时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td className="font-mono text-xs">{o.order_no}</td>
                <td>{o.package_id}</td>
                <td>{o.store_id}</td>
                <td>{o.quantity}</td>
                <td>{formatMoney(o.total_amount)}</td>
                <td>{FULFILL_TEXT[o.fulfillment_type] ?? o.fulfillment_type}</td>
                <td>{STATUS_TEXT[o.status] ?? o.status}</td>
                <td>{o.pickup_status ? PICKUP_TEXT[o.pickup_status] ?? o.pickup_status : '-'}</td>
                <td>{formatTime(o.created_at)}</td>
                <td>
                  {canPickup(o) && (
                    <button className="btn-primary" onClick={() => handlePickup(o, nextPickup(o))}>
                      {nextPickup(o) === 'ready' ? '标记备好' : '标记已取'}
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {!loading && orders.length === 0 && (
              <tr>
                <td colSpan={10} className="text-center text-gray-400 py-6">
                  暂无订单
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
