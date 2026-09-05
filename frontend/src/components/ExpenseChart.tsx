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
import type { Expense } from '../api/client'

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

export default function ExpenseChart({ rows }: { rows: Expense[] }) {
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

  if (data.length === 0) {
    return <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-400">No expenses yet.</div>
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Legend />
          {categoryList.map((cat, i) => (
            <Bar key={cat} dataKey={cat} stackId="expenses" fill={colorFor(cat, i)} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
