import { useState } from 'react'
import { getSchedule } from '../../api/schedule'
import Layout from '../../components/Layout'
import SlotChip from '../../components/SlotChip'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import EmptyState from '../../components/EmptyState'
import { Search, CalendarDays, CheckCircle, XCircle } from 'lucide-react'

function getTodayStr() {
  return new Date().toISOString().split('T')[0]
}

export default function Schedule() {
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
      const res = await getSchedule(date)
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
      <div className="max-w-3xl">
        <div className="mb-7">
          <h1 className="text-2xl font-bold text-white">Doctor Schedule</h1>
          <p className="text-slate-400 text-sm mt-0.5">Check slot availability for any date</p>
        </div>

        {/* Date picker + search */}
        <div className="card mb-6">
          <div className="flex gap-3 items-end flex-col sm:flex-row">
            <div className="flex-1 w-full">
              <label htmlFor="schedule-date" className="label">Select Date</label>
              <input
                id="schedule-date"
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
              Check Slots
            </button>
          </div>
        </div>

        <ErrorBanner message={error} onRetry={handleSearch} />

        {loading && <LoadingSpinner text="Fetching schedule..." />}

        {!loading && data && (
          <>
            {/* Stats row */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="card text-center">
                <p className="text-2xl font-bold text-white">{data.total_slots}</p>
                <p className="text-xs text-slate-400 mt-0.5 font-medium flex items-center justify-center gap-1">
                  <CalendarDays className="w-3 h-3" /> Total Slots
                </p>
              </div>
              <div className="card text-center">
                <p className="text-2xl font-bold text-emerald-400">{data.available_count}</p>
                <p className="text-xs text-slate-400 mt-0.5 font-medium flex items-center justify-center gap-1">
                  <CheckCircle className="w-3 h-3 text-emerald-500" /> Available
                </p>
              </div>
              <div className="card text-center">
                <p className="text-2xl font-bold text-red-400">{data.booked_count}</p>
                <p className="text-xs text-slate-400 mt-0.5 font-medium flex items-center justify-center gap-1">
                  <XCircle className="w-3 h-3 text-red-500" /> Booked
                </p>
              </div>
            </div>

            {/* Free slots */}
            <div className="card mb-5">
              <h2 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                Free Slots ({data.available_count})
              </h2>
              {data.free_slots.length === 0 ? (
                <p className="text-slate-500 text-sm">No free slots available.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {data.free_slots.map((slot) => (
                    <SlotChip key={slot} slot={slot} selected={false} taken={false} onClick={() => {}} />
                  ))}
                </div>
              )}
            </div>

            {/* Booked slots */}
            <div className="card">
              <h2 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                <XCircle className="w-4 h-4 text-red-400" />
                Booked Slots ({data.booked_count})
              </h2>
              {data.booked_slots.length === 0 ? (
                <p className="text-slate-500 text-sm">No slots booked yet.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {data.booked_slots.map((slot) => (
                    <SlotChip key={slot} slot={slot} selected={false} taken={true} onClick={() => {}} />
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {!loading && !data && searched && !error && (
          <EmptyState title="No data" description="Try selecting a different date." />
        )}
      </div>
    </Layout>
  )
}
