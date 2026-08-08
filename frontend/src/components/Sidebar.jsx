import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { X } from 'lucide-react'

const patientNav = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" />
      </svg>
    ),
  },
  {
    to: '/book',
    label: 'Book Appointment',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4M12 14v4M10 16h4" />
      </svg>
    ),
  },
  {
    to: '/my-appointments',
    label: 'My Appointments',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4" /><path d="M8.5 15l2 2 4 -4" />
      </svg>
    ),
  },
  {
    to: '/schedule',
    label: 'Schedule',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M8 3v4M2 9h20M5 5h14a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2H5a2 2 0 0 1 -2 -2V7a2 2 0 0 1 2 -2Z" />
        <path d="M16 3v4" /><circle cx="15.5" cy="15.5" r="3.2" /><path d="M15.5 14.2v1.3l.9 .9" />
      </svg>
    ),
  },
]

const doctorNav = [
  {
    to: '/doctor/dashboard',
    label: 'Dashboard',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" />
      </svg>
    ),
  },
  {
    to: '/doctor/schedule',
    label: "Today's Schedule",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" />
      </svg>
    ),
  },
]

const LogoutIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" />
  </svg>
)

export default function Sidebar({ onClose }) {
  const location = useLocation()
  const { role, logout } = useAuth()

  const navItems = role === 'doctor' ? doctorNav : patientNav

  const handleLogout = () => {
    logout()
  }

  return (
    <aside className="cc-sidebar">
      {/* Brand */}
      <div className="brand" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '11px' }}>
          <div className="logo-mark">
            <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 12h4l2 -6 4 12 2 -6h8" />
            </svg>
          </div>
          <span className="logo-word">City<em>Care</em></span>
        </div>
        {/* Close button for mobile */}
        {onClose && (
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--ink-faint)', display: 'flex', alignItems: 'center' }}
            className="lg:hidden"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Role badge */}
      <div className={`role-badge ${role === 'doctor' ? 'doctor' : 'patient'}`}>
        <span className="dot" />
        {role === 'doctor' ? 'Doctor' : 'Patient'}
      </div>

      {/* Nav */}
      <nav className="cc-nav">
        {navItems.map(({ to, label, icon }) => {
          const active = location.pathname === to
          return (
            <Link
              key={to}
              to={to}
              onClick={onClose}
              className={active ? 'active' : ''}
            >
              {icon}
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="cc-sidebar-foot">
        <Link to="/login" onClick={handleLogout}>
          <LogoutIcon />
          Log out
        </Link>
      </div>
    </aside>
  )
}
