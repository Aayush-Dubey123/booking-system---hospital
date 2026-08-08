import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard } from '../../api/dashboard'
import { getMyAppointments } from '../../api/appointmentApi'
import Layout from '../../components/Layout'
import DashboardCard from '../../components/DashboardCard'
import AppointmentCard from '../../components/AppointmentCard'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorBanner from '../../components/ErrorBanner'
import EmptyState from '../../components/EmptyState'
import {
  CalendarDays, CalendarCheck, CalendarX,
  LayoutGrid, CalendarClock, RefreshCw, User, Calendar, Plus
} from 'lucide-react'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
    setLoading(true)
    setError('')
    try {
      const [dashRes, apptRes] = await Promise.all([
        getDashboard(),
        getMyAppointments()
      ])
      setData(dashRes.data)
      const sorted = [...apptRes.data].sort(
        (a, b) => new Date(b.appointment_date) - new Date(a.appointment_date)
      )
      setAppointments(sorted)
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
  
  const upcoming = appointments.filter(a => new Date(a.appointment_date) >= new Date(new Date().toISOString().split('T')[0]))
  const past = appointments.filter(a => new Date(a.appointment_date) < new Date(new Date().toISOString().split('T')[0]))

  return (
    <Layout title="Medical Dashboard">
      <ErrorBanner message={error} onRetry={fetchData} />

      {loading ? (
        <LoadingSpinner text="Loading your dashboard..." />
      ) : (
        <div className="space-y-8 animate-slide-in">
          {/* Hero Section */}
          <div className="bg-blue-600 rounded-3xl p-8 md:p-10 text-white flex flex-col md:flex-row items-center justify-between shadow-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 w-80 h-80 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
            <div className="absolute bottom-0 left-10 w-40 h-40 bg-blue-400/20 rounded-full blur-2xl translate-y-1/2"></div>
            <div className="relative z-10 space-y-2">
              <p className="text-blue-100 font-medium tracking-wide">Good Morning,</p>
              <h1 className="text-3xl md:text-5xl font-bold tracking-tight">John Doe 👋</h1>
              <div className="flex items-center gap-2 text-sm text-blue-100 bg-black/10 w-fit px-3 py-1.5 rounded-full mt-4 backdrop-blur-sm">
                <User className="w-4 h-4" />
                Patient
              </div>
            </div>
            <div className="relative z-10 mt-6 md:mt-0 opacity-90 hidden md:block">
               <Calendar className="w-32 h-32 text-white/20" strokeWidth={1} />
            </div>
          </div>

          {/* Statistics */}
          <div>
             <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-slate-800">Overview</h2>
                <button onClick={fetchData} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                  <RefreshCw className="w-5 h-5" />
                </button>
             </div>
             <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                {cards.map((card) => (
                  <DashboardCard key={card.label} {...card} />
                ))}
             </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upcoming Appointments */}
            <div>
              <div className="flex items-center justify-between mb-4">
                 <h2 className="text-lg font-bold text-slate-800">Upcoming Appointments</h2>
                 <Link to="/book" className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1">
                   <Plus className="w-4 h-4" /> Book New
                 </Link>
              </div>
              <div className="space-y-4">
                {upcoming.length > 0 ? (
                  upcoming.slice(0, 3).map(appt => <AppointmentCard key={appt.id} appt={appt} />)
                ) : (
                  <EmptyState title="No upcoming visits" description="You have no upcoming appointments scheduled." />
                )}
              </div>
            </div>

            {/* Recent Appointments */}
            <div>
              <div className="flex items-center justify-between mb-4">
                 <h2 className="text-lg font-bold text-slate-800">Recent Appointments</h2>
                 <Link to="/my-appointments" className="text-sm font-medium text-blue-600 hover:text-blue-700">View All</Link>
              </div>
              <div className="space-y-4">
                {past.length > 0 ? (
                  past.slice(0, 3).map(appt => <AppointmentCard key={appt.id} appt={appt} />)
                ) : (
                  <EmptyState title="No past visits" description="Your appointment history is clean." />
                )}
              </div>
            </div>
          </div>

        </div>
      )}
    </Layout>
  )
}
