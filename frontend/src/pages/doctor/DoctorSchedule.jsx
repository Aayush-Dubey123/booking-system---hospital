import { useState } from 'react'
import { getDoctorSchedule } from '../../api/doctorApi'
import Layout from '../../components/Layout'
import PulseDivider from '../../components/PulseDivider'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import EmptyState from '../../components/EmptyState'
import { Search, CalendarDays } from 'lucide-react'

const DOCTOR_NAME = 'Dr. Amruta'
const DOCTOR_INITIALS = 'AM'
const TOTAL_SLOTS_PER_DAY = 12 // Hardcoded constant matching existing app logic

/* Flat doctor illustration (shared) */
function DoctorArt() {
  return (
    <svg viewBox="0 0 220 230" style={{ width: '100%', height: 'auto', maxWidth: 190 }}>
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

function getAvatarStyle(name) {
  // Simple hash to pick a consistent color per patient
  const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  const styles = [
    { background: 'var(--teal-tint)',  color: 'var(--teal-deep)' },
    { background: 'var(--pulse-tint)', color: 'var(--pulse-deep)' },
    { background: 'var(--amber-tint)', color: 'var(--amber)' },
    { background: 'var(--surface-tint)', color: 'var(--ink-soft)' },
  ]
  return styles[hash % styles.length]
}

function getStatusClass(status) {
  if (status === 'booked')     return 'confirmed'
  if (status === 'cancelled')  return 'cancelled'
  if (status === 'completed')  return 'confirmed'
  return 'waiting'
}

export default function DoctorSchedule() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [schedule, setSchedule] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!date) return

    setLoading(true)
    setError('')
    setHasSearched(true)
    
    try {
      const res = await getDoctorSchedule(date)
      setSchedule(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to load schedule.')
    } finally {
      setLoading(false)
    }
  }

  const bookedCount = schedule.length
  const openCount = Math.max(0, TOTAL_SLOTS_PER_DAY - bookedCount)

  // Format date for display in the panel head
  const displayDate = new Date(date).toLocaleDateString('en-US', {
    weekday: 'short', month: 'short', day: 'numeric'
  })

  return (
    <Layout title="Schedule">
      <div className="page-head">
        <div>
          <h1>Schedule</h1>
          <p>Manage your daily appointments.</p>
        </div>
        <div className="profile-chip">
          <div className="avatar" style={{ background: 'var(--pulse-tint)', color: 'var(--pulse-deep)' }}>
            {DOCTOR_INITIALS}
          </div>
          <span>{DOCTOR_NAME}</span>
        </div>
      </div>
      
      <PulseDivider animKey="schedule" />

      {/* Hero Banner (Always shown, stats reflect search results or placeholders) */}
      <div className="hero section-gap">
        <div className="hero-left">
          <h2>Good morning, {DOCTOR_NAME}</h2>
          <p>
            {hasSearched && !loading
              ? `You have ${bookedCount} appointment${bookedCount !== 1 ? 's' : ''} on this date.`
              : 'Select a date below to view your schedule.'}
          </p>
          <div className="hero-pills">
            <div className="hero-pill">
              <div className="ic">
                <CalendarDays size={17} color="#fff" />
              </div>
              <div>
                <div className="num">
                  {hasSearched && !loading ? String(bookedCount).padStart(2, '0') : '—'}
                </div>
                <div className="lbl">Booked today</div>
              </div>
            </div>
            <div className="hero-pill">
              <div className="ic">
                <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 3" />
                </svg>
              </div>
              <div>
                <div className="num">
                  {hasSearched && !loading ? String(openCount).padStart(2, '0') : '—'}
                </div>
                <div className="lbl">Slots open</div>
              </div>
            </div>
          </div>
        </div>
        <div className="hero-art">
          <DoctorArt />
        </div>
      </div>

      <ErrorBanner message={error} onRetry={handleSearch} />

      {/* Date Picker Panel */}
      <div className="section-gap">
        <form onSubmit={handleSearch} className="panel" style={{ padding: '24px 30px' }}>
          <div className="date-bar">
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
            <button type="submit" disabled={loading || !date}>
              {loading ? 'Loading…' : (
                <>
                  <Search size={16} /> View schedule
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Appointments List Panel */}
      {hasSearched && (
        <div className="section-gap">
          <div className="panel">
            <div className="panel-head">
              <div className="t">
                <CalendarDays size={18} />
                <h2>Appointments for {displayDate}</h2>
              </div>
              {!loading && schedule.length > 0 && (
                <span className="tag">{schedule.length} total</span>
              )}
            </div>
            <div className="panel-body" style={{ paddingTop: 6, paddingBottom: 6 }}>
              {loading ? (
                <div style={{ padding: '40px 0' }}>
                  <LoadingSpinner message="Loading schedule…" />
                </div>
              ) : schedule.length > 0 ? (
                schedule.map((appt, i) => {
                  const initials = appt.patient_name
                    .split(' ')
                    .map(w => w[0])
                    .join('')
                    .toUpperCase()
                    .slice(0, 2)
                    
                  return (
                    <div key={i} className="appt-row">
                      <div className="appt-time">{appt.slot}</div>
                      <div className="appt-avatar" style={getAvatarStyle(appt.patient_name)}>
                        {initials}
                      </div>
                      <div className="appt-info">
                        <p className="name">{appt.patient_name}</p>
                        <p className="reason">{appt.reason}</p>
                      </div>
                      <div className={`appt-status ${getStatusClass(appt.status)}`}>
                        {appt.status.charAt(0).toUpperCase() + appt.status.slice(1)}
                      </div>
                    </div>
                  )
                })
              ) : (
                <EmptyState
                  title="No appointments"
                  description="Your schedule is clear for this date."
                />
              )}
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
