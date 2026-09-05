import { TriangleAlert } from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Expense, ExpenseAnomaly } from '../api/client'

const CATEGORY_COLORS: Record<string, string> = {
  fuel: '#2563eb',
  service: '#16a34a',
  misc: '#d97706',
  consumables: '#9333ea',
}

function colorFor(category: string, index: number) {
  const palette = ['#2563eb', '#16a34a', '#d97706', '#9333ea', '#0891b2', '#dc2626']
  return CATEGORY_COLORS[category] ?? palette[index % palette.length]
}

function AnomalyTick({ x, y, payload, anomalyMonths }: any) {
  const isAnomalous = anomalyMonths.has(payload.value)
  return (
    <text
      x={x}
      y={y + 12}
      textAnchor="middle"
      fontSize={12}
      fontWeight={isAnomalous ? 700 : 400}
      fill={isAnomalous ? '#dc2626' : '#475569'}
    >
      {isAnomalous ? `⚠ ${payload.value}` : payload.value}
    </text>
  )
}

export default function ExpenseChart({ rows, anomalies = [] }: { rows: Expense[]; anomalies?: ExpenseAnomaly[] }) {
  const byMonth = new Map<string, Record<string, number>>()
  const categories = new Set<string>()

  for (const row of rows) {
    const month = row.date.slice(0, 7)
    categories.add(row.category)
    const entry = byMonth.get(month) ?? {}
    entry[row.category] = (entry[row.category] ?? 0) + row.amount
    byMonth.set(month, entry)
  }

  const data = Array.from(byMonth.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, values]) => ({ month, ...values }))

  const categoryList = Array.from(categories)
  const anomalyMonths = new Set(anomalies.map((a) => a.month))

  if (data.length === 0) {
    return <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-400">No expenses yet.</div>
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="month" height={28} tick={<AnomalyTick anomalyMonths={anomalyMonths} />} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {categoryList.map((cat, i) => (
            <Bar key={cat} dataKey={cat} stackId="expenses" fill={colorFor(cat, i)} />
          ))}
        </BarChart>
      </ResponsiveContainer>

      {anomalies.length > 0 && (
        <div className="mt-3 space-y-1 border-t border-slate-100 pt-3">
          {anomalies.map((a, i) => (
            <div key={i} className="flex items-center gap-2 text-xs text-red-600">
              <TriangleAlert size={13} />
              <span>
                <strong className="capitalize">{a.category}</strong> in {a.month} was ₹{a.amount.toLocaleString()} -{' '}
                {a.ratio}x the usual ₹{Math.round(a.trailing_avg).toLocaleString()}, worth a look.
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
