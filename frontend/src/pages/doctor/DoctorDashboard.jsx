import { useEffect, useState } from 'react'
import { getDoctorDashboard } from '../../api/doctorApi'
import Layout from '../../components/Layout'
import MetricTile from '../../components/MetricTile'
import PulseDivider from '../../components/PulseDivider'
import ErrorBanner from '../../components/ErrorBanner'
import { useAuth } from '../../context/AuthContext'
import { Users, CalendarDays, CalendarClock, Calendar } from 'lucide-react'

/* Shared flat doctor illustration */
function DoctorArt() {
  return (
    <svg viewBox="0 0 220 230" style={{ width: '100%', height: 'auto' }}>
      <ellipse cx="110" cy="205" rx="90" ry="14" fill="#0A5646" opacity=".35" />
      <rect x="30" y="70" width="60" height="60" rx="10" fill="#DCEEE8" />
      <path d="M40 70 h40 v-6 a20 20 0 0 0 -40 0 z" fill="#F1D9C6" />
      <circle cx="60" cy="55" r="20" fill="#F1D9C6" />
      <path d="M42 50 a18 14 0 0 1 36 0" fill="#2A2018" />
      <rect x="80" y="88" width="112" height="90" rx="14" fill="#0E6E5C" />
      <circle cx="136" cy="70" r="22" fill="#F1D9C6" />
      <path d="M116 66 a20 15 0 0 1 40 0" fill="#2A2018" />
      <rect x="105" y="90" width="62" height="88" rx="12" fill="#FFFFFF" />
      <rect x="118" y="108" width="36" height="6" rx="3" fill="#D9E5E0" />
      <rect x="118" y="120" width="36" height="6" rx="3" fill="#D9E5E0" />
      <rect x="118" y="132" width="22" height="6" rx="3" fill="#E1583F" />
      <circle cx="70" cy="115" r="7" fill="none" stroke="#0A5646" strokeWidth="3" />
      <path d="M70 122 v14 a10 10 0 0 0 10 10 h6" fill="none" stroke="#0A5646" strokeWidth="3" strokeLinecap="round" />
      <circle cx="90" cy="147" r="5" fill="#E1583F" />
    </svg>
  )
}

export default function DoctorDashboard() {
  const { token } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchDashboard = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getDoctorDashboard()
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to load dashboard.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboard()
  }, [])

  const doctorName = 'Dr. Doctor One'
  const doctorInitials = 'D1'
  const hospitalName = data?.hospital_name ?? 'Your Hospital'
  const todaysVisits = data?.todays_visits ?? null
  const appointments = data?.appointments ?? []

  return (
    <Layout title="Dashboard">
      <ErrorBanner message={error} onRetry={fetchDashboard} />

      <div className="page-head">
        <div>
          <h1>Dashboard</h1>
          <p>
            {data?.hospital_name
              ? `${data.hospital_name} — clinic overview and patient statistics.`
              : 'Clinic overview and patient statistics.'}
          </p>
        </div>
        <div className="profile-chip">
          <div className="avatar" style={{ background: 'var(--pulse-tint)', color: 'var(--pulse-deep)' }}>
            {doctorInitials}
          </div>
          <span>{doctorName}</span>
        </div>
      </div>

      <PulseDivider animKey={loading ? 'loading' : 'loaded'} />

      <div className="hero section-gap">
        <div className="hero-left">
          <div className="hero-eyebrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" />
            </svg>
            {new Date().toLocaleDateString('en-US', { weekday: 'long', day: 'numeric', month: 'long' })}
          </div>
          <h2>Good morning, {doctorName}</h2>
          <p>
            {todaysVisits != null
              ? `You have ${todaysVisits} patient${todaysVisits !== 1 ? 's' : ''} scheduled for today at ${hospitalName}.`
              : 'Loading your schedule…'}
          </p>
          <div className="hero-pills">
            <div className="role-badge doctor" style={{ margin: 0, padding: '8px 14px', fontSize: 13 }}>
              <span className="dot" />
              Doctor
            </div>
            {data?.hospital_name && (
              <div className="role-badge" style={{ margin: 0, padding: '8px 14px', fontSize: 13, background: 'var(--teal-tint)', color: 'var(--teal-deep)' }}>
                🏥 {data.hospital_name}
              </div>
            )}
          </div>
        </div>
        <div className="hero-art">
          <DoctorArt />
        </div>
      </div>

      <div className="tile-grid section-gap">
        <MetricTile
          label="Total patients"
          value={loading ? null : (data?.total_patients ?? '—')}
          icon={Users}
          variant="teal"
        />
        <MetricTile
          label="Today's visits"
          value={loading ? null : (data?.todays_visits ?? '—')}
          icon={CalendarDays}
          variant="pulse"
        />
        <MetricTile
          label="Upcoming visits"
          value={loading ? null : (data?.upcoming_visits ?? '—')}
          icon={CalendarClock}
          variant="amber"
        />
      </div>

      {/* Appointments for this hospital */}
      <div className="panel section-gap">
        <div className="panel-head">
          <div className="t">
            <Calendar size={18} />
            <h2>Hospital Appointments ({appointments.length})</h2>
          </div>
        </div>
        <div className="panel-body">
          {loading ? (
            <p style={{ color: 'var(--ink-soft)' }}>Loading appointments…</p>
          ) : appointments.length === 0 ? (
            <p style={{ color: 'var(--ink-soft)' }}>No appointments found for this hospital yet.</p>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
              {appointments.map(a => (
                <li key={a.id} style={{ padding: 12, border: '1px solid var(--line)', borderRadius: 8 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontWeight: 500, color: 'var(--ink)' }}>
                        {a.appointment_date} at {a.slot}
                      </div>
                      <div style={{ fontSize: 13, color: 'var(--ink-soft)', marginTop: 4 }}>
                        Patient: {a.patient_name}<br />
                        Doctor: {a.doctor_name || 'Pending Assignment'}<br />
                        Reason: {a.reason}
                      </div>
                    </div>
                    <span className={`status-badge ${a.status}`}>{a.status}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </Layout>
  )
}
