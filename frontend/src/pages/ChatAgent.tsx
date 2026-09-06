import { MessageSquarePlus, Trash2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import {
  confirmAction,
  deleteChatSession,
  getChatHistory,
  getChatSessions,
  sendChatMessage,
  type ChatSession,
} from '../api/client'
import ChatBubble, { type ChatDisplayMessage } from '../components/ChatBubble'
import ConfirmActionModal from '../components/ConfirmActionModal'
import { ACTIVE_VEHICLE_ID } from '../hooks/useVehicle'

const TOOL_LABELS: Record<string, string> = {
  get_vehicle_profile: 'Checking vehicle profile...',
  update_odometer: 'Updating odometer...',
  get_preferences: 'Reading your preferences...',
  check_maintenance_due: 'Checking maintenance status...',
  check_tyre_age: 'Checking tyre age...',
  check_battery_age: 'Checking battery age...',
  check_documents: 'Checking document expiry...',
  check_recalls: 'Checking for possible recalls...',
  get_weather: 'Checking the weather...',
  find_service_centers: 'Finding nearby service centers...',
  calculate_expenses: 'Calculating expenses...',
  compute_health_score: 'Computing vehicle health score...',
  prepare_trip: 'Preparing your trip checklist...',
  detect_expense_anomalies: 'Scanning for unusual expenses...',
  breakdown_recovery: 'Pulling up breakdown guidance...',
  create_service_appointment: 'Booking service appointment...',
  add_expense: 'Logging expense...',
  schedule_reminder: 'Scheduling reminder...',
}

const GREETING: ChatDisplayMessage = { kind: 'agent', text: "Hi, I'm DriveOps. Ask me anything about your vehicle." }
const SESSION_STORAGE_KEY = 'driveops_chat_session_id'

function labelFor(name: string) {
  return TOOL_LABELS[name] ?? `Running ${name}...`
}

function readSavedSessionId(): string | null {
  try {
    return localStorage.getItem(SESSION_STORAGE_KEY)
  } catch {
    return null
  }
}

function saveSessionId(id: string) {
  try {
    localStorage.setItem(SESSION_STORAGE_KEY, id)
  } catch {
    // per-viewer convenience only - a resumed conversation just won't survive a reload
  }
}

function clearSavedSessionId() {
  try {
    localStorage.removeItem(SESSION_STORAGE_KEY)
  } catch {
    // nothing to clean up if storage was never writable
  }
}

function formatRelativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diffMs / 60_000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days === 1) return 'yesterday'
  if (days < 7) return `${days}d ago`
  return new Date(iso).toLocaleDateString()
}

export default function ChatAgent() {
  const [messages, setMessages] = useState<ChatDisplayMessage[]>([GREETING])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | undefined>(undefined)
  const [busy, setBusy] = useState(false)
  const [pendingAction, setPendingAction] = useState<{ tool_name: string; args: Record<string, unknown> } | null>(null)
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [sessionsLoading, setSessionsLoading] = useState(true)

  const loadSessions = () => {
    getChatSessions(ACTIVE_VEHICLE_ID)
      .then((res) => setSessions(res.data))
      .catch(() => {})
      .finally(() => setSessionsLoading(false))
  }

  useEffect(() => {
    loadSessions()
    const saved = readSavedSessionId()
    if (!saved) return
    getChatHistory(saved)
      .then((res) => {
        if (res.data.length > 0) {
          setSessionId(saved)
          setMessages(res.data.map((m) => ({ kind: m.kind, text: m.text }) as ChatDisplayMessage))
        } else {
          clearSavedSessionId()
        }
      })
      .catch(() => clearSavedSessionId())
  }, [])

  const openSession = (id: string) => {
    if (id === sessionId || busy) return
    setBusy(true)
    getChatHistory(id)
      .then((res) => {
        setSessionId(id)
        saveSessionId(id)
        setMessages(
          res.data.length > 0
            ? res.data.map((m) => ({ kind: m.kind, text: m.text }) as ChatDisplayMessage)
            : [GREETING],
        )
        setPendingAction(null)
      })
      .finally(() => setBusy(false))
  }

  const send = async (text: string) => {
    setMessages((m) => [...m, { kind: 'user', text }])
    setBusy(true)
    setMessages((m) => [...m, { kind: 'tool_activity', label: 'DriveOps is reasoning...', pending: true }])
    try {
      const res = await sendChatMessage(ACTIVE_VEHICLE_ID, text, sessionId)
      setSessionId(res.data.session_id)
      saveSessionId(res.data.session_id)
      setMessages((m) => [
        ...m.filter((msg) => msg.kind !== 'tool_activity'),
        ...res.data.tool_calls.map((name) => ({ kind: 'tool_activity', label: labelFor(name) }) as ChatDisplayMessage),
        { kind: 'agent', text: res.data.reply },
      ])
      setPendingAction(res.data.needs_confirmation ? res.data.proposed_action : null)
      loadSessions()
    } catch {
      setMessages((m) => [
        ...m.filter((msg) => msg.kind !== 'tool_activity'),
        { kind: 'agent', text: 'Something went wrong reaching DriveOps. Is the backend running?' },
      ])
    } finally {
      setBusy(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const text = input.trim()
    if (!text || busy) return
    setInput('')
    send(text)
  }

  const handleConfirm = async (confirm: boolean) => {
    if (!sessionId) return
    setBusy(true)
    try {
      const res = await confirmAction(ACTIVE_VEHICLE_ID, sessionId, confirm)
      setMessages((m) => [
        ...m,
        ...res.data.tool_calls.map((name) => ({ kind: 'tool_activity', label: labelFor(name) }) as ChatDisplayMessage),
        { kind: 'agent', text: res.data.reply },
      ])
      setPendingAction(null)
      loadSessions()
    } finally {
      setBusy(false)
    }
  }

  const startNewConversation = () => {
    clearSavedSessionId()
    setSessionId(undefined)
    setMessages([GREETING])
    setPendingAction(null)
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('Delete this conversation? This cannot be undone.')) return
    try {
      await deleteChatSession(ACTIVE_VEHICLE_ID, id)
      setSessions((s) => s.filter((session) => session.id !== id))
      if (id === sessionId) startNewConversation()
    } catch {
      // leave the list as-is - the item will just still be there to retry
    }
  }

  return (
    <div className="flex h-full gap-4">
      <aside className="flex w-64 shrink-0 flex-col rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-100 p-3">
          <button
            onClick={startNewConversation}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            <MessageSquarePlus size={16} /> New conversation
          </button>
        </div>
        <div className="flex-1 space-y-1 overflow-y-auto p-2">
          {sessionsLoading ? (
            <p className="px-2 py-2 text-xs text-slate-400">Loading...</p>
          ) : sessions.length === 0 ? (
            <p className="px-2 py-2 text-xs text-slate-400">No conversations yet.</p>
          ) : (
            sessions.map((s) => (
              <div key={s.id} className="group relative">
                <button
                  onClick={() => openSession(s.id)}
                  className={`w-full rounded-lg py-2 pl-3 pr-8 text-left text-sm transition-colors ${
                    s.id === sessionId ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <div className="truncate font-medium">{s.preview || 'New conversation'}</div>
                  <div className={`text-xs ${s.id === sessionId ? 'text-slate-300' : 'text-slate-400'}`}>
                    {formatRelativeTime(s.updated_at)}
                  </div>
                </button>
                <button
                  onClick={(e) => handleDelete(s.id, e)}
                  aria-label="Delete conversation"
                  className={`absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 opacity-0 transition-opacity group-hover:opacity-100 ${
                    s.id === sessionId ? 'text-slate-300 hover:text-white' : 'text-slate-400 hover:text-red-600'
                  }`}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <h1 className="mb-4 text-xl font-semibold text-slate-900">Chat with DriveOps</h1>

        <div className="flex-1 space-y-2 overflow-y-auto rounded-xl border border-slate-200 bg-white p-4">
          {messages.map((m, i) => (
            <ChatBubble key={i} message={m} />
          ))}
        </div>

        <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your vehicle..."
            disabled={busy}
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={busy}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>

      <ConfirmActionModal
        open={!!pendingAction}
        title={`Agent wants to: ${pendingAction?.tool_name ?? ''}`}
        description="Confirm this action before DriveOps executes it."
        details={pendingAction?.args as Record<string, unknown> | undefined}
        busy={busy}
        onConfirm={() => handleConfirm(true)}
        onCancel={() => handleConfirm(false)}
      />
    </div>
  )
}
