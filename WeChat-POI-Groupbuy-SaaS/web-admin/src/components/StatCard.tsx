interface StatCardProps {
  title: string
  value: string
  hint?: string
  accent?: string
}

/** 指标卡片。 */
export default function StatCard({ title, value, hint, accent }: StatCardProps) {
  return (
    <div className="card">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-semibold mt-1" style={accent ? { color: accent } : undefined}>
        {value}
      </div>
      {hint && <div className="text-xs text-gray-400 mt-1">{hint}</div>}
    </div>
  )
}
