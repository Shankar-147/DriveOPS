import { useEffect, useState } from 'react'
import { addDocument, getDocuments, type DocumentStatus } from '../api/client'
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

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Documents</h1>

      <div className="grid gap-3 sm:grid-cols-3">
        {loading ? (
          <div className="text-sm text-slate-400">Loading...</div>
        ) : (
          docs.map((doc) => (
            <div key={doc.id} className={`rounded-xl border p-4 ${STATUS_STYLES[doc.status]}`}>
              <div className="text-sm font-semibold">{doc.type}</div>
              <div className="mt-1 text-xs">Expires: {doc.expiry_date}</div>
              <div className="mt-2 text-xs font-medium">
                {doc.status === 'expired'
                  ? `Expired ${Math.abs(doc.days_remaining)} days ago`
                  : `${doc.days_remaining} days remaining`}
              </div>
            </div>
          ))
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
