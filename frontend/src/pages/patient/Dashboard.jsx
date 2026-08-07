import { useEffect, useState } from 'react'
import { getDashboard } from '../../api/dashboard'
import Layout from '../../components/Layout'
import DashboardCard from '../../components/DashboardCard'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import {
  CalendarDays, CalendarCheck, CalendarX,
  LayoutGrid, CalendarClock, RefreshCw,
} from 'lucide-react'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await getDashboard()
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to load dashboard.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const cards = data ? [
    { label: 'Total Appointments', value: data.total_appointments, icon: CalendarDays, color: 'blue' },
    { label: "Today's Appointments", value: data.todays_appointments, icon: CalendarClock, color: 'violet' },
    { label: "Today's Booked Slots", value: data.todays_booked_slots, icon: CalendarCheck, color: 'amber' },
    { label: "Today's Free Slots", value: data.todays_free_slots, icon: CalendarX, color: 'green' },
    { label: 'Total Slots Per Day', value: data.total_slots_per_day, icon: LayoutGrid, color: 'rose' },
  ] : []

  return (
    <Layout>
      <div className="flex items-center justify-between mb-7">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
          <p className="text-slate-500 text-sm mt-0.5">Clinic statistics overview</p>
        </div>
        <button onClick={fetchData} className="btn-secondary text-sm gap-1.5">
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      <ErrorBanner message={error} onRetry={fetchData} />

      {loading ? (
        <LoadingSpinner text="Loading statistics..." />
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
