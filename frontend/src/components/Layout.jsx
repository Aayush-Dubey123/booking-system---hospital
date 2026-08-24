import { useState } from 'react'
import Sidebar from './Sidebar'
import { Menu } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

function getInitials(name) {
  if (!name) return '??'
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export default function Layout({ children, title = 'Overview' }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { role } = useAuth()

  const userName = role === 'doctor' ? 'Dr. Amruta' : 'John Doe'
  const initials = getInitials(userName)

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)' }}>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)', zIndex: 40 }}
          className="lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        style={{ zIndex: 50, height: '100vh', display: 'flex', flexDirection: 'column' }}
        className={`fixed inset-y-0 left-0 transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar onClose={() => setMobileOpen(false)} />
      </div>

      {/* Main content */}
      <main style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', height: '100vh', overflowY: 'auto' }}>

        {/* Page content */}
        <div style={{ padding: '32px 40px 60px', flex: 1, maxWidth: '1220px', width: '100%' }}
          className="max-lg:p-6"
        >
          {children}
        </div>
      </main>
    </div>
  )
}
