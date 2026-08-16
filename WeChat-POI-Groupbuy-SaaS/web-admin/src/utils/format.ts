// 通用格式化工具：金额（分→元）、时间（ISO UTC→本地展示）。

/** 分 → 元，保留两位小数，如 19900 → "199.00"。 */
export function formatYuan(cents: number | null | undefined): string {
  if (cents == null) return '0.00'
  return (cents / 100).toFixed(2)
}

/** 带「¥」前缀的金额展示。 */
export function formatMoney(cents: number | null | undefined): string {
  return `¥${formatYuan(cents)}`
}

/** ISO 时间 → 本地可读时间；非法返回 '-'。 */
export function formatTime(iso?: string | null): string {
  if (!iso) return '-'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '-'
  const pad = (n: number) => String(n).padStart(2, '0')
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}`
  )
}

/** 今天的 YYYY-MM-DD，用于日期筛选默认值。 */
export function todayStr(): string {
  const d = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
