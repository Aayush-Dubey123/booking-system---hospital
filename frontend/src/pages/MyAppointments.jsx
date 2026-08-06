import { useEffect, useState } from 'react'
import { getMyAppointments } from '../api/appointment'
import Sidebar from '../components/Sidebar'
import AppointmentCard from '../components/AppointmentCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorBanner from '../components/ErrorBanner'
import EmptyState from '../components/EmptyState'
import { RefreshCw } from 'lucide-react'

export default function MyAppointments() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetch = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getMyAppointments()
      // Newest first by appointment_date
      const sorted = [...res.data].sort(
        (a, b) => new Date(b.appointment_date) - new Date(a.appointment_date)
      )
      setAppointments(sorted)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to load appointments.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetch() }, [])

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="flex items-center justify-between mb-7">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">My Appointments</h1>
            <p className="text-slate-500 text-sm mt-0.5">All your scheduled visits</p>
          </div>
          <button onClick={fetch} className="btn-secondary text-sm">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        <ErrorBanner message={error} onRetry={fetch} />

        {loading ? (
          <LoadingSpinner text="Loading your appointments..." />
        ) : appointments.length === 0 ? (
          <EmptyState
            title="No appointments yet"
            description="Book your first appointment to get started."
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {appointments.map((appt) => (
              <AppointmentCard key={appt.id} appt={appt} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
