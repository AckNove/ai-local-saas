import { useEffect, useState } from 'react'
import { getMetrics } from '../api/dashboard'
import { ApiError } from '../api/client'
import type { Metrics } from '../types'
import { formatMoney, todayStr } from '../utils/format'
import StatCard from '../components/StatCard'
import Bar from '../components/Bar'

// 数据看板（T09）：销量 / 核销率 / GMV / 渠道占比，支持时间范围筛选。
export default function DataDashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [dateFrom, setDateFrom] = useState(() => {
    const d = new Date()
    d.setDate(1)
    return d.toISOString().slice(0, 10)
  })
  const [dateTo, setDateTo] = useState(todayStr())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const m = await getMetrics({ date_from: dateFrom || undefined, date_to: dateTo || undefined })
      setMetrics(m)
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

  return (
    <div>
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <h2 className="text-lg font-semibold">数据看板</h2>
        <div className="flex items-center gap-2">
          <input
            type="date"
            className="input w-40"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
          />
          <span className="text-gray-400">至</span>
          <input
            type="date"
            className="input w-40"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
          />
          <button className="btn-primary" onClick={load} disabled={loading}>
            查询
          </button>
        </div>
      </div>

      {error && <div className="text-red-500 text-sm mb-3">{error}</div>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
        <StatCard title="销量（件）" value={metrics ? String(metrics.sales_volume) : '—'} />
        <StatCard
          title="GMV"
          value={metrics ? formatMoney(metrics.gmv) : '—'}
          accent="#07c160"
        />
        <StatCard title="已支付订单" value={metrics ? String(metrics.paid_orders) : '—'} />
        <StatCard title="已核销" value={metrics ? String(metrics.verified_count) : '—'} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <div className="text-sm font-medium mb-3">转化率指标</div>
          {metrics ? (
            <>
              <Bar label="核销率" value={metrics.verify_rate} percent color="#07c160" />
              <Bar label="自提转化" value={metrics.self_pickup_rate} percent color="#3b82f6" />
              <Bar label="内容引流占比" value={metrics.video_channel_rate} percent color="#f59e0b" />
              <Bar label="订座转化" value={metrics.reservation_rate} percent color="#8b5cf6" />
            </>
          ) : (
            <div className="text-gray-400 text-sm">加载中…</div>
          )}
        </div>

        <div className="card">
          <div className="text-sm font-medium mb-3">订座概览</div>
          {metrics ? (
            <>
              <StatCard title="预约总数" value={String(metrics.reservation_total)} />
              <div className="mt-3">
                <Bar label="订座活跃率" value={metrics.reservation_rate} percent color="#8b5cf6" />
              </div>
              <div className="mt-4 text-xs text-gray-400 leading-relaxed">
                内容引流占比 = 来源为「视频号」的已支付订单 ÷ 总已支付订单；
                核销率 = 已核销核销码 ÷ 需核销订单（堂食/自提）；
                自提转化 = 自提已支付订单 ÷ 总已支付订单。
              </div>
            </>
          ) : (
            <div className="text-gray-400 text-sm">加载中…</div>
          )}
        </div>
      </div>
    </div>
  )
}
