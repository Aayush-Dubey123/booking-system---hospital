import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import {
  LayoutDashboard, CalendarPlus, CalendarCheck,
  Stethoscope, LogOut, HeartPulse, X, Users,
  CalendarClock,
} from 'lucide-react'

const patientNav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/book', label: 'Book Appointment', icon: CalendarPlus },
  { to: '/my-appointments', label: 'My Appointments', icon: CalendarCheck },
  { to: '/schedule', label: 'Schedule', icon: Stethoscope },
]

const doctorNav = [
  { to: '/doctor/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/doctor/schedule', label: "Today's Schedule", icon: CalendarClock },
]

export default function Sidebar({ onClose }) {
  const location = useLocation()
  const { role, logout } = useAuth()

  const navItems = role === 'doctor' ? doctorNav : patientNav

  const handleLogout = () => {
    logout()
  }

  return (
    <aside className="w-64 min-h-screen bg-white border-r border-slate-100 flex flex-col shadow-sm">
      {/* Logo */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-blue-600 rounded-xl flex items-center justify-center">
            <HeartPulse className="w-4 h-4 text-white" />
          </div>
          <span className="text-base font-bold text-slate-800">CityCare</span>
        </div>
        {/* Close button for mobile */}
        {onClose && (
          <button
            onClick={onClose}
            className="lg:hidden p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4 text-slate-500" />
          </button>
        )}
      </div>

      {/* Role badge */}
      <div className="px-6 pt-4 pb-2">
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold ${
          role === 'doctor'
            ? 'bg-violet-50 text-violet-700'
            : 'bg-blue-50 text-blue-700'
        }`}>
          {role === 'doctor' ? <Stethoscope className="w-3 h-3" /> : <Users className="w-3 h-3" />}
          {role === 'doctor' ? 'Doctor' : 'Patient'}
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-4 py-4 space-y-1.5">
        {navItems.map(({ to, label, icon: Icon }) => {
          const active = location.pathname === to
          return (
            <Link
              key={to}
              to={to}
              onClick={onClose}
              className={`relative flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all duration-200
                ${active
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                  : 'text-slate-500 hover:bg-slate-50 hover:text-blue-700'
                }`}
            >
              {active && (
                 <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-white rounded-r-md"></div>
              )}
              <Icon className={`w-5 h-5 ${active ? 'text-white' : 'text-slate-400 group-hover:text-blue-500'}`} />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="px-3 py-4 border-t border-slate-100">
        <Link
          to="/login"
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium text-slate-500 hover:bg-red-50 hover:text-red-600 transition-all duration-200"
        >
          <LogOut className="w-5 h-5 text-slate-400" />
          Logout
        </Link>
      </div>
    </aside>
  )
}
