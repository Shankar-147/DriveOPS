import { useEffect, useState } from 'react'
import {
  createAppointment,
  getAppointments,
  getServiceCenters,
  type Appointment,
  type ServiceCenter,
} from '../api/client'
import ConfirmActionModal from '../components/ConfirmActionModal'
import { ACTIVE_VEHICLE_ID } from '../hooks/useVehicle'

const STATUS_STYLES: Record<string, string> = {
  requested: 'bg-amber-50 text-amber-700 border-amber-200',
  confirmed: 'bg-green-50 text-green-700 border-green-200',
  cancelled: 'bg-slate-50 text-slate-500 border-slate-200',
}

export default function Appointments() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [serviceType, setServiceType] = useState('general_service')
  const [centers, setCenters] = useState<ServiceCenter[] | null>(null)
  const [searching, setSearching] = useState(false)
  const [pendingBooking, setPendingBooking] = useState<{ center: ServiceCenter; slot: string } | null>(null)
  const [saving, setSaving] = useState(false)

  const loadAppointments = () => {
    getAppointments(ACTIVE_VEHICLE_ID).then((res) => setAppointments(res.data))
  }

  useEffect(loadAppointments, [])

  const handleFindCenters = async () => {
    setSearching(true)
    try {
      const res = await getServiceCenters(ACTIVE_VEHICLE_ID, serviceType)
      setCenters(res.data.results)
    } finally {
      setSearching(false)
    }
  }

  const handleConfirmBooking = async () => {
    if (!pendingBooking) return
    setSaving(true)
    try {
      await createAppointment(ACTIVE_VEHICLE_ID, {
        provider: pendingBooking.center.name,
        date: pendingBooking.slot,
        service: serviceType,
        cost: pendingBooking.center.estimated_cost,
      })
      setPendingBooking(null)
      loadAppointments()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Appointments</h1>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Date</th>
              <th className="px-4 py-2">Provider</th>
              <th className="px-4 py-2">Service</th>
              <th className="px-4 py-2">Cost</th>
              <th className="px-4 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {appointments.length === 0 ? (
              <tr><td className="px-4 py-3 text-slate-400" colSpan={5}>No appointments yet.</td></tr>
            ) : (
              appointments.map((a) => (
                <tr key={a.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{a.date}</td>
                  <td className="px-4 py-2">{a.provider}</td>
                  <td className="px-4 py-2 capitalize">{a.service.replace('_', ' ')}</td>
                  <td className="px-4 py-2">{a.cost != null ? `₹${a.cost.toLocaleString()}` : '-'}</td>
                  <td className="px-4 py-2">
                    <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[a.status] ?? ''}`}>
                      {a.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold text-slate-900">Find a Service Center</h2>
        <div className="mt-3 flex gap-2">
          <select
            value={serviceType}
            onChange={(e) => setServiceType(e.target.value)}
            className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
          >
            <option value="general_service">General Service</option>
            <option value="tyre">Tyre</option>
            <option value="battery">Battery</option>
            <option value="towing">Towing</option>
          </select>
          <button
            onClick={handleFindCenters}
            disabled={searching}
            className="rounded-lg bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
        </div>

        {centers && (
          <div className="mt-4 space-y-2">
            {centers.length === 0 && <p className="text-sm text-slate-400">No centers found for this service.</p>}
            {centers.map((c) => (
              <div key={c.name} className="rounded-lg border border-slate-200 p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-slate-900">{c.name}</div>
                    <div className="text-xs text-slate-500">
                      {c.type} · {c.distance_km}km · {c.rating}⭐ · ₹{c.estimated_cost.toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {c.available_slots.map((slot) => (
                    <button
                      key={slot}
                      onClick={() => setPendingBooking({ center: c, slot })}
                      className="rounded-lg border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700 hover:bg-slate-100"
                    >
                      Book {slot.replace('T', ' ')}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <ConfirmActionModal
        open={!!pendingBooking}
        title="Agent wants to: Book Appointment"
        description="Confirm this booking before it's recorded."
        details={
          pendingBooking
            ? {
                Provider: pendingBooking.center.name,
                Slot: pendingBooking.slot.replace('T', ' '),
                'Estimated Cost': `₹${pendingBooking.center.estimated_cost.toLocaleString()}`,
              }
            : undefined
        }
        busy={saving}
        onConfirm={handleConfirmBooking}
        onCancel={() => setPendingBooking(null)}
      />
    </div>
  )
}
