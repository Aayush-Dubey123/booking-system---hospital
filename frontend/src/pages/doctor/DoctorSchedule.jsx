import { useState } from 'react'
import { getDoctorSchedule } from '../../api/doctorApi'
import Layout from '../../components/Layout'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import EmptyState from '../../components/EmptyState'
import { Search, Thermometer } from 'lucide-react'

function getTodayStr() {
  return new Date().toISOString().split('T')[0]
}

const statusBadge = (status) => {
  const map = {
    booked: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-red-100 text-red-700',
    completed: 'bg-blue-100 text-blue-700',
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize ${map[status] ?? 'bg-slate-100 text-slate-600'}`}>
      {status}
    </span>
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
    <Layout>
      <div className="mb-7">
        <h1 className="text-2xl font-bold text-slate-800">Today's Schedule</h1>
        <p className="text-slate-500 text-sm mt-0.5">View patient appointments by date</p>
      </div>

      {/* Date picker + search */}
      <div className="card mb-6">
        <div className="flex gap-3 items-end flex-col sm:flex-row">
          <div className="flex-1 w-full">
            <label htmlFor="doctor-schedule-date" className="label">Select Date</label>
            <input
              id="doctor-schedule-date"
              type="date"
              className="input"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={loading || !date}
            className="btn-primary w-full sm:w-auto"
          >
            <Search className="w-4 h-4" />
            View Schedule
          </button>
        </div>
      </div>

      <ErrorBanner message={error} onRetry={handleSearch} />

      {loading && <LoadingSpinner text="Fetching schedule..." />}

      {!loading && data && data.length > 0 && (
        <div className="card overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  <th className="text-left px-5 py-3.5 font-semibold text-slate-600 text-xs uppercase tracking-wider">Patient Name</th>
                  <th className="text-left px-5 py-3.5 font-semibold text-slate-600 text-xs uppercase tracking-wider">Date</th>
                  <th className="text-left px-5 py-3.5 font-semibold text-slate-600 text-xs uppercase tracking-wider">Slot</th>
                  <th className="text-left px-5 py-3.5 font-semibold text-slate-600 text-xs uppercase tracking-wider">Reason</th>
                  <th className="text-left px-5 py-3.5 font-semibold text-slate-600 text-xs uppercase tracking-wider">Symptoms</th>
                  <th className="text-left px-5 py-3.5 font-semibold text-slate-600 text-xs uppercase tracking-wider">Temp</th>
                  <th className="text-left px-5 py-3.5 font-semibold text-slate-600 text-xs uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.map((row, idx) => (
                  <tr
                    key={idx}
                    className="hover:bg-blue-50/40 transition-colors duration-100"
                  >
                    <td className="px-5 py-3.5 font-medium text-slate-800 whitespace-nowrap">{row.patient_name}</td>
                    <td className="px-5 py-3.5 text-slate-600 whitespace-nowrap">{row.appointment_date}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg text-xs font-semibold">
                        {row.slot}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-600 max-w-[200px] truncate">{row.reason}</td>
                    <td className="px-5 py-3.5 text-slate-500 max-w-[200px] truncate">{row.symptoms}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 text-slate-600">
                        <Thermometer className="w-3.5 h-3.5 text-slate-400" />
                        {row.temperature}°C
                      </span>
                    </td>
                    <td className="px-5 py-3.5">{statusBadge(row.status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Summary footer */}
          <div className="bg-slate-50 px-5 py-3 border-t border-slate-100 text-xs text-slate-500 font-medium">
            Showing {data.length} appointment{data.length !== 1 ? 's' : ''} for {date}
          </div>
        </div>
      )}

      {!loading && data && data.length === 0 && (
        <EmptyState
          title="No appointments"
          description={`No appointments scheduled for ${date}.`}
        />
      )}

      {!loading && !data && searched && !error && (
        <EmptyState title="No data" description="Try selecting a different date." />
      )}
    </Layout>
  )
}
