import { Route, Routes } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import TopBar from './components/layout/TopBar'
import Appointments from './pages/Appointments'
import ChatAgent from './pages/ChatAgent'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Expenses from './pages/Expenses'
import ServiceHistory from './pages/ServiceHistory'
import Settings from './pages/Settings'
import VehicleProfile from './pages/VehicleProfile'

export default function App() {
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/vehicle" element={<VehicleProfile />} />
            <Route path="/service-history" element={<ServiceHistory />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/appointments" element={<Appointments />} />
            <Route path="/chat" element={<ChatAgent />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
