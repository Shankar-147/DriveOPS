import { useState } from 'react'
import { updateOdometer } from '../api/client'
import { useVehicle } from '../hooks/useVehicle'

export default function VehicleProfile() {
  const { vehicle, loading, error, refresh } = useVehicle()
  const [km, setKm] = useState('')
  const [saving, setSaving] = useState(false)

  if (loading) return <div className="text-sm text-slate-400">Loading...</div>
  if (error || !vehicle) return <div className="text-sm text-red-600">{error ?? 'Vehicle not found.'}</div>

  const handleUpdateOdometer = async () => {
    const value = Number(km)
    if (!Number.isFinite(value) || value <= 0) return
    setSaving(true)
    try {
      await updateOdometer(vehicle.id, value)
      setKm('')
      refresh()
    } finally {
      setSaving(false)
    }
  }

  const fields: [string, string | number | null][] = [
    ['Make', vehicle.make],
    ['Model', vehicle.model],
    ['Variant', vehicle.variant],
    ['Year', vehicle.year],
    ['Fuel', vehicle.fuel],
    ['Odometer (km)', vehicle.odometer_km.toLocaleString()],
    ['Purchase Date', vehicle.purchase_date],
    ['Last Service Date', vehicle.last_service_date],
    ['Last Service Odometer', vehicle.last_service_odometer],
    ['Next Service Due (km)', vehicle.next_service_km],
    ['Tyre Change Date', vehicle.tyre_change_date],
    ['Battery Install Date', vehicle.battery_install_date],
  ]

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Vehicle Profile</h1>

      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 rounded-xl border border-slate-200 bg-white p-6">
        {fields.map(([label, value]) => (
          <div key={label}>
            <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</dt>
            <dd className="text-sm text-slate-800">{value ?? '-'}</dd>
          </div>
        ))}
      </dl>

      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold text-slate-900">Update Odometer</h2>
        <div className="mt-3 flex gap-2">
          <input
            type="number"
            value={km}
            onChange={(e) => setKm(e.target.value)}
            placeholder="Current km"
            className="w-40 rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
          />
          <button
            onClick={handleUpdateOdometer}
            disabled={saving}
            className="rounded-lg bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Update'}
          </button>
        </div>
      </div>
    </div>
  )
}
