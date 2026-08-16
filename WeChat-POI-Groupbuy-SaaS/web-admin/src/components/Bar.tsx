interface BarProps {
  label: string
  /** 0~1 的比率，或任意数值（配合 max）。 */
  value: number
  max?: number
  /** 显示为百分比（乘以 100 并加 %）。 */
  percent?: boolean
  color?: string
}

/** 轻量横向条形图（无第三方图表库依赖）。 */
export default function Bar({ label, value, max = 1, percent, color = '#07c160' }: BarProps) {
  const ratio = max > 0 ? Math.min(1, Math.max(0, value / max)) : 0
  const text = percent ? `${(value * 100).toFixed(1)}%` : String(value)
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-800">{text}</span>
      </div>
      <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${ratio * 100}%`, background: color }}
        />
      </div>
    </div>
  )
}
