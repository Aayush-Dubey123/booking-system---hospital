import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard } from '../../api/dashboard'
import { getMyAppointments } from '../../api/appointmentApi'
import Layout from '../../components/Layout'
import AppointmentCard from '../../components/AppointmentCard'
import MetricTile from '../../components/MetricTile'
import PulseDivider from '../../components/PulseDivider'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import EmptyState from '../../components/EmptyState'
import {
  CalendarDays, CalendarCheck, CalendarX, LayoutGrid, CalendarClock, Plus,
} from 'lucide-react'

const USER_NAME = 'John Doe'
const USER_INITIALS = 'JD'

function getTodayLabel() {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
  })
}

/* Flat doctor illustration (shared with auth shell) */
function DoctorArt() {
  return (
    <svg viewBox="0 0 220 230" style={{ width: '100%', height: 'auto' }}>
      <ellipse cx="110" cy="205" rx="90" ry="14" fill="#cca75a" opacity=".2" />
      <rect x="30" y="70" width="60" height="60" rx="10" fill="#0b1329" />
      <path d="M40 70 h40 v-6 a20 20 0 0 0 -40 0 z" fill="#F1D9C6" />
      <circle cx="60" cy="55" r="20" fill="#F1D9C6" />
      <path d="M42 50 a18 14 0 0 1 36 0" fill="#2A2018" />
      <rect x="80" y="88" width="112" height="90" rx="14" fill="#cca75a" />
      <circle cx="136" cy="70" r="22" fill="#F1D9C6" />
      <path d="M116 66 a20 15 0 0 1 40 0" fill="#2A2018" />
      <rect x="105" y="90" width="62" height="88" rx="12" fill="#080f1e" stroke="rgba(204, 167, 90, 0.25)" strokeWidth="1" />
      <rect x="118" y="108" width="36" height="6" rx="3" fill="#0b1329" />
      <rect x="118" y="120" width="36" height="6" rx="3" fill="#0b1329" />
      <rect x="118" y="132" width="22" height="6" rx="3" fill="#cca75a" />
      <circle cx="70" cy="115" r="7" fill="none" stroke="#cca75a" strokeWidth="3" />
      <path d="M70 122 v14 a10 10 0 0 0 10 10 h6" fill="none" stroke="#cca75a" strokeWidth="3" strokeLinecap="round" />
      <circle cx="90" cy="147" r="5" fill="#cca75a" />
    </svg>
  )
}

/* Skeleton visit rows shown while loading */
function SkeletonRows() {
  return (
    <>
      {[1, 2, 3].map((i) => (
        <div key={i} className="visit-row skeleton">
          <div className="visit-avatar" />
          <div className="visit-info" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div className="skel-line" style={{ width: '60%' }} />
            <div className="skel-line" style={{ width: '40%' }} />
          </div>
          <div className="skel-line" style={{ width: 80 }} />
          <div className="skel-line" style={{ width: 64, borderRadius: 999 }} />
        </div>
      ))}
    </>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [dashRes, apptRes] = await Promise.all([
        getDashboard(),
        getMyAppointments(),
      ])
      setData(dashRes.data)
      const sorted = [...apptRes.data].sort(
        (a, b) => new Date(b.appointment_date) - new Date(a.appointment_date)
      )
      setAppointments(sorted)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to load dashboard.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const upcoming = appointments.filter(
    (a) => new Date(a.appointment_date) >= new Date(new Date().toISOString().split('T')[0])
  )

  const todayCount = data?.todays_appointments ?? null
  const totalCount = data?.total_appointments ?? null

  return (
    <Layout title="Dashboard">
      <ErrorBanner message={error} onRetry={fetchData} />

      {/* Page head */}
      <div className="page-head">
        <div>
          <h1>Dashboard</h1>
          <p>Here's what's happening at the clinic today.</p>
        </div>
        <div className="profile-chip">
          <div className="avatar">{USER_INITIALS}</div>
          <span>{USER_NAME}</span>
        </div>
      </div>

      {/* EKG divider */}
      <PulseDivider animKey={loading ? 'loading' : 'loaded'} />

      {/* Hero welcome banner */}
      <div className="hero section-gap">
        <div className="hero-left">
          <div className="hero-eyebrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" />
            </svg>
            {getTodayLabel()}
          </div>
          <h2>Good morning, {USER_NAME.split(' ')[0]}</h2>
          <p>
            {todayCount != null
              ? `You have ${todayCount} visit${todayCount !== 1 ? 's' : ''} today and ${totalCount} total this month.`
              : 'Loading your schedule…'}
          </p>
          <div className="hero-pills">
            <div className="hero-pill">
              <div className="ic">
                <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4" />
                </svg>
              </div>
              <div>
                <div className="num">
                  {totalCount != null ? String(totalCount).padStart(2, '0') : '—'}
                </div>
                <div className="lbl">Total appointments</div>
              </div>
            </div>
            <div className="hero-pill">
              <div className="ic">
                <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4" /><path d="M8.5 15l2 2 4 -4" />
                </svg>
              </div>
              <div>
                <div className="num">
                  {todayCount != null ? String(todayCount).padStart(2, '0') : '—'}
                </div>
                <div className="lbl">Today's appointments</div>
              </div>
            </div>
          </div>
        </div>
        <div className="hero-art">
          <DoctorArt />
        </div>
      </div>

      {/* Metric tiles */}
      <div className="tile-grid section-gap">
        <MetricTile
          label="Today's booked slots"
          value={loading ? null : (data?.todays_booked_slots ?? '—')}
          icon={CalendarCheck}
          variant="teal"
        />
        <MetricTile
          label="Today's free slots"
          value={loading ? null : (data?.todays_free_slots ?? '—')}
          icon={CalendarX}
          variant="pulse"
        />
        <MetricTile
          label="Total slots per day"
          value={loading ? null : (data?.total_slots_per_day ?? '—')}
          icon={LayoutGrid}
          variant="amber"
        />
      </div>

      {/* Appointments panel (full width — chart omitted: no real data source) */}
      <div className="section-gap">
        <div className="panel">
          <div className="panel-head">
            <div className="t">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4" />
              </svg>
              <h2>Your appointments</h2>
            </div>
            {!loading && appointments.length > 0 && (
              <span className="tag">{appointments.length} total</span>
            )}
            <Link
              to="/book"
              style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600, color: 'var(--teal)', textDecoration: 'none' }}
            >
              <Plus size={14} /> Book new
            </Link>
          </div>
          <div className="panel-body" style={{ paddingTop: 6, paddingBottom: 6 }}>
            {loading ? (
              <SkeletonRows />
            ) : upcoming.length > 0 ? (
              upcoming.slice(0, 5).map((appt, i) => (
                <AppointmentCard key={appt.id} appt={appt} index={i} />
              ))
            ) : appointments.length > 0 ? (
              /* Show recent if no upcoming */
              appointments.slice(0, 5).map((appt, i) => (
                <AppointmentCard key={appt.id} appt={appt} index={i} />
              ))
            ) : (
              <EmptyState
                title="No appointments yet"
                description="Book your first appointment to get started."
              />
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
