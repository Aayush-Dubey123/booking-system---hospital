import { useEffect, useState } from 'react'
import { getDoctorDashboard, acceptAppointment } from '../../api/doctorApi'
import { createPrescription } from '../../api/prescriptionApi'
import Layout from '../../components/Layout'
import MetricTile from '../../components/MetricTile'
import PulseDivider from '../../components/PulseDivider'
import ErrorBanner from '../../components/ErrorBanner'
import { useAuth } from '../../context/AuthContext'
import { Users, CalendarDays, CalendarClock, Calendar, CheckCircle, FileText, X } from 'lucide-react'

/* Shared flat doctor illustration */
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

export default function DoctorDashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Modal State
  const [activeAppt, setActiveAppt] = useState(null)
  const [diagnosis, setDiagnosis] = useState('')
  const [medicines, setMedicines] = useState('')
  const [notes, setNotes] = useState('')
  const [submittingRx, setSubmittingRx] = useState(false)
  const [rxError, setRxError] = useState('')
  const [rxSuccess, setRxSuccess] = useState('')
  const [acceptingId, setAcceptingId] = useState(null)

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

  const handleAccept = async (appointmentId) => {
    setAcceptingId(appointmentId)
    setError('')
    try {
      await acceptAppointment(appointmentId)
      await fetchDashboard()
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to accept appointment.')
    } finally {
      setAcceptingId(null)
    }
  }

  const handleOpenRxModal = (appt) => {
    setActiveAppt(appt)
    setDiagnosis('')
    setMedicines('')
    setNotes('')
    setRxError('')
    setRxSuccess('')
  }

  const handleCreatePrescription = async (e) => {
    e.preventDefault()
    if (!activeAppt || !diagnosis || !medicines) return

    setSubmittingRx(true)
    setRxError('')
    setRxSuccess('')

    try {
      const res = await createPrescription({
        appointment_id: activeAppt.id,
        diagnosis,
        medicines,
        notes,
      })
      setRxSuccess('Prescription created successfully!')
      setTimeout(() => {
        setActiveAppt(null)
        fetchDashboard()
      }, 1500)
    } catch (err) {
      setRxError(err.response?.data?.detail ?? 'Failed to create prescription.')
    } finally {
      setSubmittingRx(false)
    }
  }

  const doctorName = user ? `Dr. ${user.first_name} ${user.last_name}` : 'Dr. Doctor One'
  const doctorInitials = user ? `${user.first_name[0]}${user.last_name[0]}` : 'D1'
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
                <li key={a.id} style={{ padding: 16, border: '1px solid var(--line)', borderRadius: 10, background: '#fff' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--ink)', fontSize: 15 }}>
                        {a.appointment_date} at {a.slot}
                      </div>
                      <div style={{ fontSize: 13, color: 'var(--ink-soft)', marginTop: 4, lineHeight: 1.5 }}>
                        <strong>Patient:</strong> {a.patient_name}<br />
                        <strong>Assigned Doctor:</strong> {a.doctor_name || 'Pending Assignment'}<br />
                        <strong>Reason:</strong> {a.reason} | <strong>Symptoms:</strong> {a.symptoms} ({a.temperature}°C)
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <span className={`status-badge ${a.status}`}>{a.status}</span>
                      
                      {a.status === 'pending' && (
                        <button
                          onClick={() => handleAccept(a.id)}
                          disabled={acceptingId === a.id}
                          style={{
                            padding: '6px 14px',
                            borderRadius: 6,
                            background: 'var(--teal-deep)',
                            color: '#fff',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: 13,
                            fontWeight: 500,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6
                          }}
                        >
                          <CheckCircle size={14} />
                          {acceptingId === a.id ? 'Accepting…' : 'Accept'}
                        </button>
                      )}

                      {a.status === 'accepted' && (
                        <button
                          onClick={() => handleOpenRxModal(a)}
                          style={{
                            padding: '6px 14px',
                            borderRadius: 6,
                            background: 'var(--pulse-deep)',
                            color: '#fff',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: 13,
                            fontWeight: 500,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6
                          }}
                        >
                          <FileText size={14} />
                          Create Prescription
                        </button>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Prescription Modal */}
      {activeAppt && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, padding: 20
        }}>
          <div style={{
            background: '#fff', borderRadius: 12, width: '100%', maxWidth: 540,
            padding: 24, boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ margin: 0, fontSize: 18, color: 'var(--ink)' }}>
                Prescribe for {activeAppt.patient_name}
              </h3>
              <button onClick={() => setActiveAppt(null)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                <X size={20} color="var(--ink-soft)" />
              </button>
            </div>

            {rxError && <div style={{ background: '#FEE2E2', color: '#991B1B', padding: 10, borderRadius: 6, marginBottom: 14, fontSize: 13 }}>{rxError}</div>}
            {rxSuccess && <div style={{ background: '#D1FAE5', color: '#065F46', padding: 10, borderRadius: 6, marginBottom: 14, fontSize: 13 }}>{rxSuccess}</div>}

            <form onSubmit={handleCreatePrescription}>
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--ink)', marginBottom: 4 }}>Diagnosis *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acute Bronchitis, Fever"
                  value={diagnosis}
                  onChange={(e) => setDiagnosis(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--line)', fontSize: 14 }}
                />
              </div>

              <div style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--ink)', marginBottom: 4 }}>Medicines & Dosage *</label>
                <textarea
                  required
                  rows={4}
                  placeholder="e.g. Amoxicillin 500mg - 1 capsule thrice daily for 5 days&#10;Paracetamol 650mg - as needed for fever"
                  value={medicines}
                  onChange={(e) => setMedicines(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--line)', fontSize: 14 }}
                />
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--ink)', marginBottom: 4 }}>Instructions / Special Notes</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Drink plenty of fluids. Rest for 3 days."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--line)', fontSize: 14 }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
                <button
                  type="button"
                  onClick={() => setActiveAppt(null)}
                  style={{ padding: '8px 16px', borderRadius: 6, border: '1px solid var(--line)', background: '#fff', cursor: 'pointer', fontSize: 13 }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingRx}
                  style={{ padding: '8px 18px', borderRadius: 6, border: 'none', background: 'var(--pulse-deep)', color: '#fff', fontWeight: 500, cursor: 'pointer', fontSize: 13 }}
                >
                  {submittingRx ? 'Generating PDF & Uploading…' : 'Generate & Save Prescription'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  )
}
