import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { getSchedule } from '../../api/schedule'
import { bookAppointment } from '../../api/appointmentApi'
import { getHospitals } from '../../api/hospitalApi'
import Layout from '../../components/Layout'
import SlotChip from '../../components/SlotChip'
import PulseDivider from '../../components/PulseDivider'
import { useToast } from '../../components/Toast'
import { CheckCircle2, Loader2, Calendar } from 'lucide-react'

const USER_NAME = 'John Doe'
const USER_INITIALS = 'JD'

/* Flat doctor illustration (shared) */
function DoctorArt() {
  return (
    <svg viewBox="0 0 220 230" style={{ width: '100%', height: 'auto', maxWidth: 190 }}>
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

export default function BookAppointment() {
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm()
  const [slots, setSlots] = useState([])
  const [hospitals, setHospitals] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingHospitals, setLoadingHospitals] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState(false)
  
  // Real data for the dark side panel
  const [availableCount, setAvailableCount] = useState(null)
  const [totalSlots, setTotalSlots] = useState(null)
  
  const toast = useToast()

  const selectedDate = watch('appointment_date')
  const selectedSlot = watch('slot')
  const selectedHospital = watch('hospital_id')

  useEffect(() => {
    const fetchHospitalsList = async () => {
      try {
        const res = await getHospitals()
        setHospitals(res.data)
      } catch (err) {
        toast.error('Failed to load hospitals')
      } finally {
        setLoadingHospitals(false)
      }
    }
    fetchHospitalsList()
  }, [])

  useEffect(() => {
    if (selectedDate && selectedHospital) {
      fetchSlots(selectedDate, selectedHospital)
    } else {
      setSlots([])
      setAvailableCount(null)
    }
  }, [selectedDate, selectedHospital])

  const fetchSlots = async (date, hospitalId) => {
    setLoading(true)
    setAvailableCount(null)
    try {
      const res = await getSchedule(date, hospitalId)
      setSlots(res.data.free_slots || [])
      setAvailableCount(res.data.available_count ?? 0)
      setTotalSlots(res.data.total_slots ?? 12)
    } catch (err) {
      toast.error('Failed to load slots for this date')
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data) => {
    if (!data.slot) {
      toast.error('Please select an appointment time')
      return
    }
    setSubmitting(true)
    try {
      await bookAppointment({
        ...data,
        temperature: parseFloat(data.temperature),
      })
      setSuccess(true)
    } catch (err) {
      toast.error(err.response?.data?.detail ?? 'Failed to book appointment')
    } finally {
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <Layout title="Book Appointment">
        <div className="page-head">
          <div>
            <h1>All set.</h1>
            <p>Your appointment has been confirmed.</p>
          </div>
          <div className="profile-chip">
            <div className="avatar">{USER_INITIALS}</div>
            <span>{USER_NAME}</span>
          </div>
        </div>
        <PulseDivider animKey="success" />

        <div className="section-gap" style={{ maxWidth: 500, margin: '40px auto' }}>
          <div className="panel" style={{ textAlign: 'center', padding: '40px 30px' }}>
            <div style={{
              width: 54, height: 54, borderRadius: '50%', background: 'var(--teal-tint)', color: 'var(--teal-deep)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px'
            }}>
              <CheckCircle2 size={26} strokeWidth={2.5} />
            </div>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 24, margin: '0 0 10px', color: 'var(--ink)' }}>
              Appointment Booked
            </h2>
            <p style={{ color: 'var(--ink-soft)', margin: '0 0 24px' }}>
              We've sent a confirmation to your email. We look forward to seeing you.
            </p>
            <button
              onClick={() => { setSuccess(false); setValue('slot', '') }}
              className="btn-cc-primary"
            >
              Book another
            </button>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Book Appointment">
      <div className="page-head">
        <div>
          <h1>Book Appointment</h1>
          <p>Schedule a visit with Dr. Amruta.</p>
        </div>
        <div className="profile-chip">
          <div className="avatar">{USER_INITIALS}</div>
          <span>{USER_NAME}</span>
        </div>
      </div>
      
      <PulseDivider animKey="book" />

      <div className="section-gap max-lg:grid-cols-1 max-lg:!grid" style={{ display: 'grid', gridTemplateColumns: '1.15fr 0.85fr', gap: '16px', alignItems: 'stretch' }}>
        {/* Left column — Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="panel" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <div className="panel-head">
            <div className="t">
              <Calendar size={18} />
              <h2>Appointment details</h2>
            </div>
          </div>
          <div className="panel-body" style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            
            <div className="cc-field">
              <label htmlFor="hospital_id">Hospital</label>
              <select
                id="hospital_id"
                {...register('hospital_id', { required: 'Hospital is required' })}
              >
                <option value="">Select a hospital...</option>
                {hospitals.map(h => (
                  <option key={h.id} value={h.id}>{h.name}</option>
                ))}
              </select>
              {errors.hospital_id && <p className="auth-error">{errors.hospital_id.message}</p>}
            </div>

            <div className="cc-field" style={{ marginTop: 22 }}>
              <label htmlFor="appointment_date">Date</label>
              <input
                id="appointment_date"
                type="date"
                min={new Date().toISOString().split('T')[0]}
                {...register('appointment_date', { required: 'Date is required' })}
              />
              {errors.appointment_date && <p className="auth-error">{errors.appointment_date.message}</p>}
            </div>

            {selectedDate && selectedHospital && (
              <div className="cc-field" style={{ marginTop: 22 }}>
                <label>Available times</label>
                {loading ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--ink-soft)', fontSize: 14 }}>
                    <Loader2 size={16} className="animate-spin" /> Loading slots…
                  </div>
                ) : slots.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                    {slots.map((slot) => (
                      <SlotChip
                        key={slot}
                        slot={slot}
                        selected={selectedSlot === slot}
                        onClick={() => setValue('slot', slot)}
                      />
                    ))}
                  </div>
                ) : (
                  <p style={{ color: 'var(--pulse-deep)', fontSize: 13.5, margin: 0, padding: '12px 16px', background: 'var(--pulse-tint)', borderRadius: 'var(--radius-ctrl)' }}>
                    No slots available for this date.
                  </p>
                )}
              </div>
            )}

            <div className="cc-field" style={{ marginTop: 22 }}>
              <label htmlFor="reason">Reason for visit</label>
              <input
                id="reason"
                placeholder="e.g. Annual checkup"
                {...register('reason', { required: 'Reason is required' })}
              />
              {errors.reason && <p className="auth-error">{errors.reason.message}</p>}
            </div>

            <div className="cc-field" style={{ marginTop: 22 }}>
              <label htmlFor="symptoms">Symptoms (optional)</label>
              <textarea
                id="symptoms"
                placeholder="Briefly describe what you're experiencing…"
                {...register('symptoms')}
              />
            </div>

            <div className="cc-field" style={{ marginTop: 22 }}>
              <label htmlFor="temperature">Current Temperature (°F)</label>
              <input
                id="temperature"
                type="number"
                step="0.1"
                placeholder="98.6"
                {...register('temperature', {
                  required: 'Temperature is required',
                  min: { value: 90, message: 'Invalid temperature' },
                  max: { value: 110, message: 'Invalid temperature' },
                })}
              />
              {errors.temperature && <p className="auth-error">{errors.temperature.message}</p>}
            </div>

            <div style={{ marginTop: 32, paddingTop: 20, borderTop: '1px solid var(--line)' }}>
              <button type="submit" disabled={submitting} className="btn-cc-primary">
                {submitting ? <Loader2 size={16} className="animate-spin" /> : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: 17, height: 17 }}>
                    <path d="M5 12h14M13 6l6 6-6 6" />
                  </svg>
                )}
                {submitting ? 'Booking…' : 'Confirm appointment'}
              </button>
            </div>
          </div>
        </form>

        {/* Right column — Dark panel (Free slots) */}
        <div className="panel" style={{ background: 'var(--surface)', color: 'var(--ink)', border: '1px solid var(--line)', padding: '38px 30px', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 24 }}>
            <DoctorArt />
          </div>
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 20, fontWeight: 500, margin: '0 0 16px' }}>
            Free slots today
          </h3>
          {selectedDate ? (
            loading ? (
              <div className="skeleton-num" style={{ margin: '0 auto 8px' }} />
            ) : (
              <>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 48, fontWeight: 600, lineHeight: 1, margin: '0 0 6px', color: 'var(--teal)' }}>
                  {availableCount}
                </div>
                <div style={{ fontSize: 13, color: 'var(--ink-soft)' }}>
                  Out of {totalSlots} slots
                </div>
              </>
            )
          ) : (
            <>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 48, fontWeight: 600, lineHeight: 1, margin: '0 0 6px', color: 'var(--ink)', opacity: 0.25 }}>
                —
              </div>
              <div style={{ fontSize: 13, color: 'var(--ink-soft)' }}>
                Select a date to see availability
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  )
}
