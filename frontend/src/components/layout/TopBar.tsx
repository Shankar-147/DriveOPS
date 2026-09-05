import { Gauge } from 'lucide-react'
import { useVehicle } from '../../hooks/useVehicle'

export default function TopBar() {
  const { vehicle, loading } = useVehicle()

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
      {loading || !vehicle ? (
        <span className="text-sm text-slate-400">Loading vehicle...</span>
      ) : (
        <div className="flex items-center gap-2 text-sm text-slate-700">
          <span className="font-semibold text-slate-900">
            {vehicle.year} {vehicle.make} {vehicle.model} {vehicle.variant ?? ''}
          </span>
          <span className="text-slate-300">|</span>
          <span className="flex items-center gap-1 text-slate-500">
            <Gauge size={16} /> {vehicle.odometer_km.toLocaleString()} km
          </span>
        </div>
      )}
    </header>
  )
}
