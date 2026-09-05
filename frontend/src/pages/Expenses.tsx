import { useEffect, useState } from 'react'
import { addExpense, getExpenses, type ExpensesResponse } from '../api/client'
import ConfirmActionModal from '../components/ConfirmActionModal'
import ExpenseChart from '../components/ExpenseChart'
import { ACTIVE_VEHICLE_ID } from '../hooks/useVehicle'

const emptyForm = { date: '', category: '', amount: '', description: '' }

export default function Expenses() {
  const [data, setData] = useState<ExpensesResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(emptyForm)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    getExpenses(ACTIVE_VEHICLE_ID, 'all')
      .then((res) => setData(res.data))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleOpenConfirm = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.date || !form.category || !form.amount) return
    setConfirmOpen(true)
  }

  const handleConfirm = async () => {
    setSaving(true)
    try {
      await addExpense(ACTIVE_VEHICLE_ID, {
        date: form.date,
        category: form.category,
        amount: Number(form.amount),
        description: form.description || undefined,
      })
      setForm(emptyForm)
      setConfirmOpen(false)
      load()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-xl font-semibold text-slate-900">Expenses</h1>

      {data && <ExpenseChart rows={data.rows} anomalies={data.anomalies} />}

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Date</th>
              <th className="px-4 py-2">Category</th>
              <th className="px-4 py-2">Amount</th>
              <th className="px-4 py-2">Description</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td className="px-4 py-3 text-slate-400" colSpan={4}>Loading...</td></tr>
            ) : !data || data.rows.length === 0 ? (
              <tr><td className="px-4 py-3 text-slate-400" colSpan={4}>No expenses yet.</td></tr>
            ) : (
              data.rows.map((r) => (
                <tr key={r.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">{r.date}</td>
                  <td className="px-4 py-2 capitalize">{r.category}</td>
                  <td className="px-4 py-2">₹{r.amount.toLocaleString()}</td>
                  <td className="px-4 py-2 text-slate-600">{r.description ?? '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <form onSubmit={handleOpenConfirm} className="grid gap-3 rounded-xl border border-slate-200 bg-white p-6 sm:grid-cols-2">
        <h2 className="text-sm font-semibold text-slate-900 sm:col-span-2">Add Expense</h2>
        <input type="date" required value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="text" required placeholder="Category" value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="number" required placeholder="Amount" value={form.amount}
          onChange={(e) => setForm({ ...form, amount: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <input type="text" placeholder="Description (optional)" value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm" />
        <button type="submit"
          className="rounded-lg bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-800 sm:col-span-2 sm:w-fit">
          Add Expense
        </button>
      </form>

      <ConfirmActionModal
        open={confirmOpen}
        title="Agent wants to: Log Expense"
        description="Confirm this expense before it's recorded."
        details={{ Date: form.date, Category: form.category, Amount: `₹${form.amount}`, Description: form.description || '-' }}
        busy={saving}
        onConfirm={handleConfirm}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  )
}
