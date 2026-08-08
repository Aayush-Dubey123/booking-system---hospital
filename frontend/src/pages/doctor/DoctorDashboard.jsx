import { useEffect, useState } from 'react'
import { getDoctorDashboard } from '../../api/doctorApi'
import Layout from '../../components/Layout'
import DashboardCard from '../../components/DashboardCard'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import { Users, CalendarCheck, CalendarClock, RefreshCw, Badge as BadgeIcon, Activity } from 'lucide-react'

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
    <Layout title="Doctor Dashboard">
      <ErrorBanner message={error} onRetry={fetchData} />

      {loading ? (
        <LoadingSpinner text="Loading dashboard..." />
      ) : (
        <div className="space-y-8 animate-slide-in">
          {/* Hero Section */}
          <div className="bg-white rounded-3xl p-8 md:p-10 flex flex-col md:flex-row items-center justify-between border border-slate-100 shadow-sm relative overflow-hidden">
            <div className="relative z-10 space-y-4">
              <div className="space-y-1">
                <p className="text-slate-500 font-medium">Good Morning,</p>
                <h1 className="text-3xl md:text-4xl font-bold text-slate-800">Dr. Amruta</h1>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-sm font-semibold">
                  General Physician
                </span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-600 rounded-lg text-sm font-semibold">
                  <BadgeIcon className="w-4 h-4 text-slate-400" />
                  #CC-1042
                </span>
              </div>
            </div>
            
            <div className="relative z-10 mt-6 md:mt-0">
               <div className="w-32 h-32 md:w-40 md:h-40 bg-gradient-to-tr from-blue-100 to-indigo-50 rounded-full flex items-center justify-center p-6 shadow-inner">
                  <Activity className="w-16 h-16 md:w-20 md:h-20 text-blue-500/80" strokeWidth={1.5} />
               </div>
            </div>
            {/* Background Decoration */}
            <div className="absolute right-0 bottom-0 w-64 h-64 bg-blue-50 rounded-full blur-3xl translate-x-1/3 translate-y-1/3"></div>
          </div>

          {/* Statistics */}
          <div>
            <div className="flex items-center justify-between mb-4">
               <h2 className="text-lg font-bold text-slate-800">Overview</h2>
               <button onClick={fetchData} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                 <RefreshCw className="w-5 h-5" />
               </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {cards.map((card) => (
                <DashboardCard key={card.label} {...card} />
              ))}
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
