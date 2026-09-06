import { Pencil } from 'lucide-react'
import { useEffect, useState } from 'react'
import { addDocument, getDocuments, updateDocument, type DocumentStatus } from '../api/client'
import { ACTIVE_VEHICLE_ID } from '../hooks/useVehicle'

const STATUS_STYLES: Record<DocumentStatus['status'], string> = {
  valid: 'border-green-200 bg-green-50 text-green-700',
  expiring_soon: 'border-amber-200 bg-amber-50 text-amber-700',
  expired: 'border-red-200 bg-red-50 text-red-700',
}

const emptyForm = { type: '', issue_date: '', expiry_date: '' }

export default function Documents() {
  const [docs, setDocs] = useState<DocumentStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)

  const [editingId, setEditingId] = useState<number | null>(null)
  const [editForm, setEditForm] = useState({ type: '', expiry_date: '' })
  const [editSaving, setEditSaving] = useState(false)

  const load = () => {
    setLoading(true)
    getDocuments(ACTIVE_VEHICLE_ID)
      .then((res) => setDocs(res.data))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.type || !form.expiry_date) return
    setSaving(true)
    try {
      await addDocument(ACTIVE_VEHICLE_ID, {
        type: form.type,
        issue_date: form.issue_date || undefined,
        expiry_date: form.expiry_date,
      })
      setForm(emptyForm)
      load()
    } finally {
      setSaving(false)
    }
  }

  const startEdit = (doc: DocumentStatus) => {
    setEditingId(doc.id)
    setEditForm({ type: doc.type, expiry_date: doc.expiry_date })
  }

  const handleSaveEdit = async (docId: number) => {
    if (!editForm.type || !editForm.expiry_date) return
    setEditSaving(true)
    try {
      await updateDocument(docId, { type: editForm.type, expiry_date: editForm.expiry_date })
      setEditingId(null)
      load()
    } finally {
      setEditSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Documents</h1>

      <div className="grid gap-3 sm:grid-cols-3">
        {loading ? (
          <div className="text-sm text-slate-400">Loading...</div>
        ) : (
          docs.map((doc) =>
            editingId === doc.id ? (
              <div key={doc.id} className="space-y-2 rounded-xl border border-slate-300 bg-white p-4">
                <input
                  type="text"
                  value={editForm.type}
                  onChange={(e) => setEditForm({ ...editForm, type: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-2 py-1 text-sm"
                />
                <input
                  type="date"
                  value={editForm.expiry_date}
                  onChange={(e) => setEditForm({ ...editForm, expiry_date: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 px-2 py-1 text-sm"
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSaveEdit(doc.id)}
                    disabled={editSaving}
                    className="rounded-lg bg-slate-900 px-3 py-1 text-xs font-medium text-white hover:bg-slate-800 disabled:opacity-50"
                  >
                    {editSaving ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    className="rounded-lg px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div key={doc.id} className={`relative rounded-xl border p-4 ${STATUS_STYLES[doc.status]}`}>
                <button
                  onClick={() => startEdit(doc)}
                  className="absolute right-3 top-3 text-current opacity-60 hover:opacity-100"
                  aria-label="Edit document"
                >
                  <Pencil size={14} />
                </button>
                <div className="text-sm font-semibold">{doc.type}</div>
                <div className="mt-1 text-xs">Expires: {doc.expiry_date}</div>
                <div className="mt-2 text-xs font-medium">
                  {doc.status === 'expired'
                    ? `Expired ${Math.abs(doc.days_remaining)} days ago`
                    : `${doc.days_remaining} days remaining`}
                </div>
              </div>
            ),
          )
        )}
      </div>

      <form onSubmit={handleSubmit} className="grid gap-3 rounded-xl border border-slate-200 bg-white p-6 sm:grid-cols-3">
        <h2 className="text-sm font-semibold text-slate-900 sm:col-span-3">Add Document</h2>
        <input type="text" required placeholder="Type (e.g. Insurance)" value={form.type}
          onChange={(e) => setForm({ ...form, type: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="date" placeholder="Issue date" value={form.issue_date}
          onChange={(e) => setForm({ ...form, issue_date: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="date" required placeholder="Expiry date" value={form.expiry_date}
          onChange={(e) => setForm({ ...form, expiry_date: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <button type="submit" disabled={saving}
          className="rounded-lg bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 sm:col-span-3 sm:w-fit">
          {saving ? 'Saving...' : 'Add Document'}
        </button>
      </form>
    </div>
  )
}
