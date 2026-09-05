import { useState } from 'react'
import { confirmAction, sendChatMessage } from '../api/client'
import ChatBubble, { type ChatDisplayMessage } from '../components/ChatBubble'
import ConfirmActionModal from '../components/ConfirmActionModal'
import { ACTIVE_VEHICLE_ID } from '../hooks/useVehicle'

export default function ChatAgent() {
  const [messages, setMessages] = useState<ChatDisplayMessage[]>([
    { kind: 'agent', text: "Hi, I'm DriveOps. Ask me anything about your vehicle." },
  ])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | undefined>(undefined)
  const [busy, setBusy] = useState(false)
  const [pendingAction, setPendingAction] = useState<{ tool_name: string; args: Record<string, unknown> } | null>(null)

  const send = async (text: string) => {
    setMessages((m) => [...m, { kind: 'user', text }])
    setBusy(true)
    setMessages((m) => [...m, { kind: 'tool_activity', label: 'DriveOps is reasoning...', pending: true }])
    try {
      const res = await sendChatMessage(ACTIVE_VEHICLE_ID, text, sessionId)
      setSessionId(res.data.session_id)
      setMessages((m) => [
        ...m.filter((msg) => msg.kind !== 'tool_activity'),
        ...(res.data.needs_confirmation
          ? [{ kind: 'tool_activity', label: `Proposed action: ${res.data.proposed_action?.tool_name}` } as ChatDisplayMessage]
          : []),
        { kind: 'agent', text: res.data.reply },
      ])
      setPendingAction(res.data.needs_confirmation ? res.data.proposed_action : null)
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
      setMessages((m) => [...m, { kind: 'agent', text: res.data.reply }])
      setPendingAction(null)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-2xl flex-col">
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
