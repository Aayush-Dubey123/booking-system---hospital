import { useState } from 'react'
import { getDoctorSchedule } from '../../api/doctorApi'
import Layout from '../../components/Layout'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import EmptyState from '../../components/EmptyState'
import { Search, Thermometer, User, Clock, FileText, Activity, Calendar as CalendarIcon } from 'lucide-react'

function getTodayStr() {
  return new Date().toISOString().split('T')[0]
}

const statusBadge = (status) => {
  const map = {
    booked: 'bg-blue-50 text-blue-700 border-blue-100',
    cancelled: 'bg-rose-50 text-rose-700 border-rose-100',
    completed: 'bg-emerald-50 text-emerald-700 border-emerald-100',
  }
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold capitalize border ${map[status] ?? 'bg-slate-50 text-slate-600 border-slate-200'}`}>
      {status}
    </span>
  )
}

function DoctorAppointmentCard({ appt }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm hover:shadow-md transition-shadow duration-300 relative overflow-hidden group flex flex-col h-full">
      <div className="absolute left-0 top-0 w-1 h-full bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400">
             <User className="w-6 h-6" />
          </div>
          <div>
            <span className="font-bold text-slate-800 text-base block">{appt.patient_name}</span>
            <span className="text-xs font-medium text-slate-500 flex items-center gap-1 mt-0.5">
              <CalendarIcon className="w-3 h-3" />
              {appt.appointment_date}
            </span>
          </div>
        </div>
        {statusBadge(appt.status)}
      </div>

      <div className="grid grid-cols-2 gap-4 bg-slate-50 rounded-xl p-4 mt-auto">
        <div className="flex items-center gap-2 text-slate-700 text-sm font-medium">
          <Clock className="w-4 h-4 text-slate-400" />
          <span className="bg-white px-2 py-0.5 rounded-md border border-slate-200 shadow-xs">{appt.slot}</span>
        </div>
        <div className="flex items-center gap-2 text-slate-700 text-sm font-medium">
          <Thermometer className="w-4 h-4 text-slate-400" />
          <span>{appt.temperature}°C</span>
        </div>
        <div className="flex flex-col gap-1 col-span-2 mt-2">
          <div className="flex items-start gap-2">
            <FileText className="w-4 h-4 text-blue-500 mt-0.5" />
            <span className="font-semibold text-slate-800 text-sm">{appt.reason}</span>
          </div>
          <div className="flex items-start gap-2 pl-6">
            <span className="text-slate-500 text-sm leading-relaxed">{appt.symptoms}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function DoctorSchedule() {
  const [date, setDate] = useState(getTodayStr())
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    if (!date) return
    setLoading(true)
    setError('')
    setSearched(true)
    try {
      const res = await getDoctorSchedule(date)
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to fetch schedule.')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout title="Today's Schedule">
      <div className="mb-8 lg:hidden">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Today's Schedule</h1>
        <p className="text-slate-500 mt-1">View patient appointments by date</p>
      </div>

      {/* Date picker + search */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mb-8 animate-slide-in">
        <div className="flex gap-4 items-end flex-col sm:flex-row">
          <div className="flex-1 w-full">
            <label htmlFor="doctor-schedule-date" className="label text-slate-600 font-semibold mb-2">Select Date</label>
            <input
              id="doctor-schedule-date"
              type="date"
              className="input bg-slate-50 border-slate-200"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={loading || !date}
            className="btn-primary w-full sm:w-auto px-8 shadow-blue-500/20 shadow-lg"
          >
            <Search className="w-4 h-4" />
            Load Board
          </button>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={handleSearch} />

      {loading && <LoadingSpinner text="Fetching appointment board..." />}

      {!loading && data && data.length > 0 && (
        <div className="animate-slide-in">
          <div className="flex items-center justify-between mb-4 px-1">
             <h2 className="text-lg font-bold text-slate-800">Appointments ({data.length})</h2>
             <span className="text-sm font-medium text-slate-500">{date}</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {data.map((row, idx) => (
              <DoctorAppointmentCard key={idx} appt={row} />
            ))}
          </div>
        </div>
      )}

      {!loading && data && data.length === 0 && (
        <EmptyState
          title="No appointments"
          description={`Your board is clear for ${date}.`}
        />
      )}

      {!loading && !data && searched && !error && (
        <EmptyState title="No data" description="Try selecting a different date." />
      )}
    </Layout>
  )
}
