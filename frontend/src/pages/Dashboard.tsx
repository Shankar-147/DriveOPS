import { Bell, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDashboard, getNotifications, markNotificationRead, type DashboardResponse, type Notification } from '../api/client'
import HealthScoreGauge from '../components/HealthScoreGauge'
import PriorityCard from '../components/PriorityCard'
import { ACTIVE_VEHICLE_ID } from '../hooks/useVehicle'

const SEVERITY_DOT: Record<Notification['severity'], string> = {
  high: 'bg-red-500',
  medium: 'bg-amber-500',
  low: 'bg-slate-400',
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    getDashboard(ACTIVE_VEHICLE_ID)
      .then((res) => setData(res.data))
      .catch(() => setError('Could not load the dashboard. Is the backend running?'))
    getNotifications(ACTIVE_VEHICLE_ID, true)
      .then((res) => setNotifications(res.data))
      .catch(() => {})
  }, [])

  const dismiss = async (id: number) => {
    setNotifications((n) => n.filter((x) => x.id !== id))
    try {
      await markNotificationRead(ACTIVE_VEHICLE_ID, id)
    } catch {
      // non-critical - if this fails the notification just reappears on next load
    }
  }

  if (error) return <div className="text-sm text-red-600">{error}</div>
  if (!data) return <div className="text-sm text-slate-400">Loading...</div>

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">What needs my attention?</h1>

      {notifications.length > 0 && (
        <div className="space-y-2 rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <Bell size={14} /> Notifications
          </div>
          {notifications.map((n) => (
            <div key={n.id} className="flex items-center justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2 text-sm">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 shrink-0 rounded-full ${SEVERITY_DOT[n.severity]}`} />
                <span className="text-slate-700">{n.message}</span>
              </div>
              <button onClick={() => dismiss(n.id)} className="text-slate-400 hover:text-slate-600" aria-label="Dismiss">
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        {data.priorities.length === 0 ? (
          <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
            Nothing needs attention right now.
          </div>
        ) : (
          data.priorities.map((p, i) => <PriorityCard key={i} {...p} />)
        )}
      </div>

      <div className="grid gap-6 rounded-xl border border-slate-200 bg-white p-6 sm:grid-cols-[1fr_auto]">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Today's recommendation
          </h2>
          <p className="mt-2 text-slate-800">{data.recommendation}</p>
          <button
            onClick={() => navigate('/chat')}
            className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Ask DriveOps
          </button>
        </div>
        <HealthScoreGauge {...data.health_score} />
      </div>
    </div>
  )
}
