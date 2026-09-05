import { AlertTriangle, Info, TriangleAlert } from 'lucide-react'
import type { Priority } from '../api/client'

const STYLES: Record<Priority['severity'], { bg: string; border: string; text: string; icon: typeof Info }> = {
  high: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: TriangleAlert },
  medium: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: AlertTriangle },
  low: { bg: 'bg-slate-50', border: 'border-slate-200', text: 'text-slate-600', icon: Info },
}

export default function PriorityCard({ severity, message }: Priority) {
  const s = STYLES[severity]
  const Icon = s.icon
  return (
    <div className={`flex items-start gap-3 rounded-lg border ${s.border} ${s.bg} px-4 py-3`}>
      <Icon size={18} className={`mt-0.5 shrink-0 ${s.text}`} />
      <div>
        <div className={`text-xs font-semibold uppercase tracking-wide ${s.text}`}>{severity}</div>
        <div className="text-sm text-slate-800">{message}</div>
      </div>
    </div>
  )
}
