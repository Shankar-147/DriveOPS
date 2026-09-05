import { useEffect, useState } from 'react'
import { addServiceRecord, getServiceHistory, type ServiceRecord } from '../api/client'
import { ACTIVE_VEHICLE_ID } from '../hooks/useVehicle'

const emptyForm = { date: '', odometer_km: '', service_type: '', cost: '', work_done: '' }

export default function ServiceHistory() {
  const [rows, setRows] = useState<ServiceRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    getServiceHistory(ACTIVE_VEHICLE_ID)
      .then((res) => setRows(res.data))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.date || !form.odometer_km || !form.service_type) return
    setSaving(true)
    try {
      await addServiceRecord(ACTIVE_VEHICLE_ID, {
        date: form.date,
        odometer_km: Number(form.odometer_km),
        service_type: form.service_type,
        cost: form.cost ? Number(form.cost) : undefined,
        work_done: form.work_done || undefined,
      })
      setForm(emptyForm)
      load()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Service History</h1>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Date</th>
              <th className="px-4 py-2">Odometer</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Cost</th>
              <th className="px-4 py-2">Work Done</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td className="px-4 py-3 text-slate-400" colSpan={5}>Loading...</td></tr>
            ) : rows.length === 0 ? (
              <tr><td className="px-4 py-3 text-slate-400" colSpan={5}>No service records yet.</td></tr>
            ) : (
              rows.map((r) => (
                <tr key={r.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{r.date}</td>
                  <td className="px-4 py-2">{r.odometer_km.toLocaleString()} km</td>
                  <td className="px-4 py-2">{r.service_type}</td>
                  <td className="px-4 py-2">{r.cost != null ? `₹${r.cost.toLocaleString()}` : '-'}</td>
                  <td className="px-4 py-2 text-slate-600">{r.work_done ?? '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <form onSubmit={handleSubmit} className="grid gap-3 rounded-xl border border-slate-200 bg-white p-6 sm:grid-cols-2">
        <h2 className="text-sm font-semibold text-slate-900 sm:col-span-2">Add Service Record</h2>
        <input type="date" required value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="number" required placeholder="Odometer (km)" value={form.odometer_km}
          onChange={(e) => setForm({ ...form, odometer_km: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="text" required placeholder="Service type" value={form.service_type}
          onChange={(e) => setForm({ ...form, service_type: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="number" placeholder="Cost (optional)" value={form.cost}
          onChange={(e) => setForm({ ...form, cost: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="text" placeholder="Work done (optional)" value={form.work_done}
          onChange={(e) => setForm({ ...form, work_done: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm sm:col-span-2" />
        <button type="submit" disabled={saving}
          className="rounded-lg bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 sm:col-span-2 sm:w-fit">
          {saving ? 'Saving...' : 'Add Record'}
        </button>
      </form>
    </div>
  )
}
