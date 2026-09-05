import { useState } from 'react'
import type { HealthScore } from '../api/client'

const LABELS: Record<string, string> = {
  maintenance: 'Maintenance',
  tyres: 'Tyres',
  battery: 'Battery',
  documents: 'Documents',
  recall: 'Recalls',
}

function colorFor(total: number) {
  if (total >= 80) return '#16a34a'
  if (total >= 60) return '#d97706'
  return '#dc2626'
}

export default function HealthScoreGauge({ total, breakdown }: HealthScore) {
  const [hover, setHover] = useState(false)
  const radius = 46
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - total / 100)
  const color = colorFor(total)

  return (
    <div
      className="relative flex flex-col items-center gap-2"
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="10" />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
        />
        <text x="60" y="65" textAnchor="middle" fontSize="24" fontWeight="600" fill="#0f172a">
          {total}
        </text>
      </svg>
      <span className="text-sm font-medium text-slate-600">Vehicle Health</span>

      {hover && (
        <div className="absolute top-full z-10 mt-2 w-48 rounded-lg border border-slate-200 bg-white p-3 shadow-lg">
          {Object.entries(breakdown).map(([key, value]) => (
            <div key={key} className="flex justify-between py-0.5 text-xs text-slate-600">
              <span>{LABELS[key] ?? key}</span>
              <span className="font-medium text-slate-900">{value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
