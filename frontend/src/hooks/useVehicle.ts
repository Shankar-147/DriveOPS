import { useEffect, useState } from 'react'
import { getVehicle, type Vehicle } from '../api/client'

export const ACTIVE_VEHICLE_ID = 'VH001'

export function useVehicle() {
  const [vehicle, setVehicle] = useState<Vehicle | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = () => {
    setLoading(true)
    getVehicle(ACTIVE_VEHICLE_ID)
      .then((res) => setVehicle(res.data))
      .catch(() => setError('Could not load vehicle profile.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    refresh()
  }, [])

  return { vehicle, loading, error, refresh }
}
