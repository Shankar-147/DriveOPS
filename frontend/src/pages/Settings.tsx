import { useEffect, useState } from 'react'
import { getPreferences, updatePreference } from '../api/client'
import { ACTIVE_VEHICLE_ID } from '../hooks/useVehicle'

const FIELDS: { key: string; label: string; type: 'select' | 'text' | 'number'; options?: string[] }[] = [
  { key: 'preferred_center', label: 'Preferred Service Center', type: 'select', options: ['authorized', 'independent', 'any'] },
  { key: 'max_auto_approve_amount', label: 'Max Auto-Approve Amount (₹)', type: 'number' },
  { key: 'preferred_days', label: 'Preferred Days', type: 'select', options: ['weekday', 'weekend', 'any'] },
]

export default function Settings() {
  const [prefs, setPrefs] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [savingKey, setSavingKey] = useState<string | null>(null)

  useEffect(() => {
    getPreferences(ACTIVE_VEHICLE_ID)
      .then((res) => setPrefs(res.data))
      .finally(() => setLoading(false))
  }, [])

  const handleChange = async (key: string, value: string) => {
    setPrefs((p) => ({ ...p, [key]: value }))
    setSavingKey(key)
    try {
      await updatePreference(ACTIVE_VEHICLE_ID, key, value)
    } finally {
      setSavingKey(null)
    }
  }

  if (loading) return <div className="text-sm text-slate-400">Loading...</div>

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Settings</h1>

      <div className="space-y-4 rounded-xl border border-slate-200 bg-white p-6">
        {FIELDS.map(({ key, label, type, options }) => (
          <div key={key}>
            <label className="block text-xs font-medium uppercase tracking-wide text-slate-400">{label}</label>
            {type === 'select' ? (
              <select
                value={prefs[key] ?? ''}
                onChange={(e) => handleChange(key, e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
              >
                {options?.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            ) : (
              <input
                type={type}
                value={prefs[key] ?? ''}
                onChange={(e) => handleChange(key, e.target.value)}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
              />
            )}
            {savingKey === key && <span className="text-xs text-slate-400">Saving...</span>}
          </div>
        ))}
      </div>
      <p className="text-xs text-slate-400">
        These preferences feed directly into DriveOps' reasoning - it reads them via a tool call, not a hardcoded rule.
      </p>
    </div>
  )
}
