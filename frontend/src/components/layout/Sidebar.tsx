import {
  Calendar,
  Car,
  FileText,
  LayoutDashboard,
  MessageCircle,
  Settings,
  Wallet,
  Wrench,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/vehicle', label: 'Vehicle Profile', icon: Car },
  { to: '/service-history', label: 'Service History', icon: Wrench },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/expenses', label: 'Expenses', icon: Wallet },
  { to: '/appointments', label: 'Appointments', icon: Calendar },
  { to: '/chat', label: 'Chat with DriveOps', icon: MessageCircle },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="px-5 py-5 text-lg font-semibold text-slate-900">DriveOps</div>
      <nav className="flex-1 space-y-1 px-3">
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
