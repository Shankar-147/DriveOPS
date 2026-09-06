import axios from 'axios'

const client = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL })

export interface Vehicle {
  id: string
  make: string
  model: string
  variant: string | null
  year: number
  fuel: string
  odometer_km: number
  purchase_date: string | null
  last_service_date: string | null
  last_service_odometer: number | null
  next_service_km: number | null
  tyre_change_date: string | null
  battery_install_date: string | null
}

export interface Priority {
  severity: 'high' | 'medium' | 'low'
  message: string
}

export interface HealthScore {
  total: number
  breakdown: Record<string, number>
}

export interface DashboardResponse {
  priorities: Priority[]
  recommendation: string
  health_score: HealthScore
  vehicle_summary: Vehicle
}

export interface ServiceRecord {
  id: number
  vehicle_id: string
  date: string
  odometer_km: number
  service_type: string
  cost: number | null
  work_done: string | null
}

export interface DocumentStatus {
  id: number
  type: string
  expiry_date: string
  days_remaining: number
  status: 'valid' | 'expiring_soon' | 'expired'
}

export interface Expense {
  id: number
  vehicle_id: string
  date: string
  category: string
  amount: number
  description: string | null
}

export interface ExpenseAnomaly {
  month: string
  category: string
  amount: number
  trailing_avg: number
  ratio: number
}

export interface ExpensesResponse {
  period: string
  total: number
  by_category: Record<string, number>
  count: number
  rows: Expense[]
  anomalies: ExpenseAnomaly[]
}

export interface Appointment {
  id: number
  vehicle_id: string
  provider: string
  date: string
  service: string
  cost: number | null
  status: string
}

export interface ServiceCenter {
  name: string
  type: string
  distance_km: number
  rating: number
  services: string[]
  estimated_cost: number
  available_slots: string[]
}

export interface Notification {
  id: number
  vehicle_id: string
  severity: 'high' | 'medium' | 'low'
  message: string
  created_at: string
  read: number
}

export interface ChatResponse {
  reply: string
  needs_confirmation: boolean
  proposed_action: { tool_name: string; args: Record<string, unknown> } | null
  session_id: string
  tool_calls: string[]
}

// Vehicle
export const getVehicle = (vehicleId: string) => client.get<Vehicle>(`/api/vehicle/${vehicleId}`)
export const getDashboard = (vehicleId: string) =>
  client.get<DashboardResponse>(`/api/vehicle/${vehicleId}/dashboard`)
export const updateOdometer = (vehicleId: string, km: number) =>
  client.post<Vehicle>(`/api/vehicle/${vehicleId}/odometer`, { km })

// Service history
export const getServiceHistory = (vehicleId: string) =>
  client.get<ServiceRecord[]>(`/api/vehicle/${vehicleId}/service-history`)
export const addServiceRecord = (
  vehicleId: string,
  record: { date: string; odometer_km: number; service_type: string; cost?: number; work_done?: string },
) => client.post<ServiceRecord>(`/api/vehicle/${vehicleId}/service-history`, record)

// Documents
export const getDocuments = (vehicleId: string) =>
  client.get<DocumentStatus[]>(`/api/vehicle/${vehicleId}/documents`)
export const addDocument = (
  vehicleId: string,
  doc: { type: string; issue_date?: string; expiry_date: string },
) => client.post(`/api/vehicle/${vehicleId}/documents`, doc)
export const updateDocument = (
  docId: number,
  fields: Partial<{ type: string; issue_date: string; expiry_date: string }>,
) => client.put(`/api/documents/${docId}`, fields)

// Expenses
export const getExpenses = (vehicleId: string, period: 'month' | 'year' | 'all' = 'all') =>
  client.get<ExpensesResponse>(`/api/vehicle/${vehicleId}/expenses`, { params: { period } })
export const addExpense = (
  vehicleId: string,
  expense: { date: string; category: string; amount: number; description?: string },
) => client.post(`/api/vehicle/${vehicleId}/expenses`, expense)

// Appointments
export const getAppointments = (vehicleId: string) =>
  client.get<Appointment[]>(`/api/vehicle/${vehicleId}/appointments`)
export const createAppointment = (
  vehicleId: string,
  appt: { provider: string; date: string; service: string; cost?: number },
) => client.post(`/api/vehicle/${vehicleId}/appointments`, appt)
export const getAppointment = (appointmentId: number) =>
  client.get<Appointment>(`/api/appointments/${appointmentId}`)
export const getServiceCenters = (vehicleId: string, serviceType: string, location = 'Chennai') =>
  client.get<{ results: ServiceCenter[] }>(`/api/vehicle/${vehicleId}/service-centers`, {
    params: { service_type: serviceType, location },
  })

// Preferences
export const getPreferences = (vehicleId: string) =>
  client.get<Record<string, string>>(`/api/vehicle/${vehicleId}/preferences`)
export const updatePreference = (vehicleId: string, key: string, value: string) =>
  client.put<Record<string, string>>(`/api/vehicle/${vehicleId}/preferences`, { key, value })

// Notifications
export const getNotifications = (vehicleId: string, unreadOnly = false) =>
  client.get<Notification[]>(`/api/vehicle/${vehicleId}/notifications`, { params: { unread_only: unreadOnly } })
export const markNotificationRead = (vehicleId: string, notificationId: number) =>
  client.put<Notification>(`/api/vehicle/${vehicleId}/notifications/${notificationId}/read`)

// Chat
export interface ChatHistoryMessage {
  kind: 'user' | 'agent'
  text: string
}

export interface ChatSession {
  id: string
  vehicle_id: string
  created_at: string
  updated_at: string
  preview: string | null
}

export const getChatSessions = (vehicleId: string) =>
  client.get<ChatSession[]>(`/api/vehicle/${vehicleId}/chat-sessions`)
export const deleteChatSession = (vehicleId: string, sessionId: string) =>
  client.delete(`/api/vehicle/${vehicleId}/chat-sessions/${sessionId}`)
export const sendChatMessage = (vehicleId: string, message: string, sessionId?: string) =>
  client.post<ChatResponse>('/api/chat', { vehicle_id: vehicleId, message, session_id: sessionId })
export const confirmAction = (vehicleId: string, sessionId: string, confirm: boolean) =>
  client.post<ChatResponse>('/api/chat/confirm', { vehicle_id: vehicleId, session_id: sessionId, confirm })
export const getChatHistory = (sessionId: string) =>
  client.get<ChatHistoryMessage[]>(`/api/chat/${sessionId}/history`)

export default client
