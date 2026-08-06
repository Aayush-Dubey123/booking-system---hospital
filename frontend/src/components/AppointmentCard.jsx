import { Calendar, Clock, Thermometer, FileText, Activity } from 'lucide-react'

const statusBadge = (status) => {
  const map = {
    booked: 'bg-emerald-100 text-emerald-700',
    cancelled: 'bg-red-100 text-red-700',
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold capitalize ${map[status] ?? 'bg-slate-100 text-slate-600'}`}>
      {status}
    </span>
  )
}

export default function AppointmentCard({ appt }) {
  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2 text-blue-600">
          <Calendar className="w-4 h-4" />
          <span className="font-semibold text-sm">{appt.appointment_date}</span>
        </div>
        {statusBadge(appt.status)}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="flex items-center gap-2 text-slate-600 text-sm">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{appt.slot}</span>
        </div>
        <div className="flex items-center gap-2 text-slate-600 text-sm">
          <Thermometer className="w-3.5 h-3.5 text-slate-400" />
          <span>{appt.temperature}°C</span>
        </div>
        <div className="flex items-start gap-2 text-slate-600 text-sm col-span-2">
          <FileText className="w-3.5 h-3.5 text-slate-400 mt-0.5" />
          <span className="font-medium">{appt.reason}</span>
        </div>
        <div className="flex items-start gap-2 text-slate-500 text-xs col-span-2">
          <Activity className="w-3.5 h-3.5 mt-0.5 shrink-0" />
          <span>{appt.symptoms}</span>
        </div>
      </div>
    </div>
  )
}
