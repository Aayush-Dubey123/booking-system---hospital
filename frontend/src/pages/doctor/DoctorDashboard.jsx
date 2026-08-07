import { useEffect, useState } from 'react'
import { getDoctorDashboard } from '../../api/doctorApi'
import Layout from '../../components/Layout'
import DashboardCard from '../../components/DashboardCard'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import { Users, CalendarCheck, CalendarClock, RefreshCw } from 'lucide-react'

export default function DoctorDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
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

  useEffect(() => { fetchData() }, [])

  const cards = data ? [
    { label: 'Total Patients', value: data.total_patients, icon: Users, color: 'blue' },
    { label: "Today's Visits", value: data.todays_visits, icon: CalendarCheck, color: 'green' },
    { label: 'Upcoming Visits', value: data.upcoming_visits, icon: CalendarClock, color: 'violet' },
  ] : []

  return (
    <Layout>
      <div className="flex items-center justify-between mb-7">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Doctor Dashboard</h1>
          <p className="text-slate-500 text-sm mt-0.5">Your practice at a glance</p>
        </div>
        <button onClick={fetchData} className="btn-secondary text-sm gap-1.5">
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      <ErrorBanner message={error} onRetry={fetchData} />

      {loading ? (
        <LoadingSpinner text="Loading dashboard..." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mt-4">
          {cards.map((card) => (
            <DashboardCard key={card.label} {...card} />
          ))}
        </div>
      )}
    </Layout>
  )
}
