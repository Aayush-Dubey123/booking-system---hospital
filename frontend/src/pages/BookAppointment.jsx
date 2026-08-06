import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { bookAppointment } from '../api/appointment'
import { getSchedule } from '../api/schedule'
import Sidebar from '../components/Sidebar'
import SlotChip from '../components/SlotChip'
import ErrorBanner from '../components/ErrorBanner'
import { Loader2, CheckCircle, CalendarPlus } from 'lucide-react'

const VALID_SLOTS = [
  '10:00', '10:30', '11:00', '11:30', '12:00', '12:30',
  '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
]

function getTodayStr() {
  return new Date().toISOString().split('T')[0]
}

function getMaxDateStr() {
  const d = new Date()
  d.setDate(d.getDate() + 7)
  return d.toISOString().split('T')[0]
}

export default function BookAppointment() {
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState('')
  const [bookedSlots, setBookedSlots] = useState([])
  const [scheduleLoading, setScheduleLoading] = useState(false)
  const navigate = useNavigate()

  const watchDate = watch('appointment_date')

  const fetchSlots = async (date) => {
    if (!date) return
    setScheduleLoading(true)
    try {
      const res = await getSchedule(date)
      setBookedSlots(res.data.booked_slots ?? [])
    } catch {
      setBookedSlots([])
    } finally {
      setScheduleLoading(false)
    }
  }

  const handleDateChange = (e) => {
    setValue('appointment_date', e.target.value)
    setSelectedSlot('')
    fetchSlots(e.target.value)
  }

  const onSubmit = async (data) => {
    if (!selectedSlot) { setError('Please select a slot.'); return }
    setLoading(true)
    setError('')
    try {
      const res = await bookAppointment({
        reason: data.reason,
        symptoms: data.symptoms,
        temperature: parseFloat(data.temperature),
        appointment_date: data.appointment_date,
        slot: selectedSlot,
      })
      setSuccess(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Booking failed.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main className="flex-1 p-8 flex items-center justify-center">
          <div className="card max-w-sm w-full text-center shadow-md">
            <div className="w-14 h-14 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-7 h-7 text-emerald-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-800 mb-1">Booking Confirmed!</h2>
            <p className="text-slate-500 text-sm mb-5">Your appointment has been booked successfully.</p>
            <div className="bg-slate-50 rounded-xl p-4 text-sm text-left space-y-2 mb-6">
              <div className="flex justify-between">
                <span className="text-slate-500">Date</span>
                <span className="font-semibold text-slate-700">{success.appointment_date}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Slot</span>
                <span className="font-semibold text-slate-700">{success.slot}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Status</span>
                <span className="font-semibold text-emerald-600 capitalize">{success.status}</span>
              </div>
            </div>
            <div className="flex gap-3">
              <button onClick={() => navigate('/my-appointments')} className="btn-primary flex-1">
                View My Appointments
              </button>
              <button onClick={() => { setSuccess(null); setSelectedSlot('') }} className="btn-secondary flex-1">
                Book Another
              </button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 p-8 max-w-2xl mx-auto w-full">
        <div className="mb-7">
          <h1 className="text-2xl font-bold text-slate-800">Book Appointment</h1>
          <p className="text-slate-500 text-sm mt-0.5">Schedule a visit with CityCare Clinic</p>
        </div>

        <ErrorBanner message={error} onRetry={null} />

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5 mt-4">
          <div className="card">
            <h2 className="font-semibold text-slate-700 mb-4 flex items-center gap-2">
              <CalendarPlus className="w-4 h-4 text-blue-500" />
              Appointment Details
            </h2>

            <div className="space-y-4">
              <div>
                <label className="label">Date</label>
                <input
                  type="date"
                  min={getTodayStr()}
                  max={getMaxDateStr()}
                  className={`input ${errors.appointment_date ? 'input-error' : ''}`}
                  {...register('appointment_date', { required: 'Date is required' })}
                  onChange={handleDateChange}
                />
                {errors.appointment_date && <p className="text-red-500 text-xs mt-1">{errors.appointment_date.message}</p>}
              </div>

              {watchDate && (
                <div>
                  <label className="label">
                    Select a Slot
                    {scheduleLoading && <span className="text-xs text-slate-400 ml-2">Loading...</span>}
                  </label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {VALID_SLOTS.map((slot) => (
                      <SlotChip
                        key={slot}
                        slot={slot}
                        selected={selectedSlot === slot}
                        taken={bookedSlots.includes(slot)}
                        onClick={() => setSelectedSlot(slot)}
                      />
                    ))}
                  </div>
                  {!selectedSlot && <p className="text-slate-400 text-xs mt-2">Click an available slot to select it</p>}
                </div>
              )}

              <div>
                <label className="label">Reason for Visit</label>
                <input
                  className={`input ${errors.reason ? 'input-error' : ''}`}
                  placeholder="e.g. Fever, headache"
                  {...register('reason', { required: 'Reason is required' })}
                />
                {errors.reason && <p className="text-red-500 text-xs mt-1">{errors.reason.message}</p>}
              </div>

              <div>
                <label className="label">Symptoms</label>
                <textarea
                  rows={3}
                  className={`input resize-none ${errors.symptoms ? 'input-error' : ''}`}
                  placeholder="Describe your symptoms..."
                  {...register('symptoms', { required: 'Symptoms are required' })}
                />
                {errors.symptoms && <p className="text-red-500 text-xs mt-1">{errors.symptoms.message}</p>}
              </div>

              <div>
                <label className="label">Temperature (°C)</label>
                <input
                  type="number"
                  step="0.1"
                  className={`input ${errors.temperature ? 'input-error' : ''}`}
                  placeholder="e.g. 37.2"
                  {...register('temperature', {
                    required: 'Temperature is required',
                    min: { value: 35, message: 'Must be ≥ 35°C' },
                    max: { value: 42, message: 'Must be ≤ 42°C' },
                  })}
                />
                {errors.temperature && <p className="text-red-500 text-xs mt-1">{errors.temperature.message}</p>}
              </div>
            </div>
          </div>

          <button type="submit" disabled={loading || !selectedSlot} className="btn-primary w-full">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            {loading ? 'Booking...' : 'Confirm Booking'}
          </button>
        </form>
      </main>
    </div>
  )
}
