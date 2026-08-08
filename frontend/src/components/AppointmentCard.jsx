import { Calendar, Clock, Thermometer, FileText, Activity } from 'lucide-react'

const statusBadge = (status) => {
  const map = {
    booked: 'bg-blue-50 text-blue-700 border-blue-100',
    cancelled: 'bg-rose-50 text-rose-700 border-rose-100',
    completed: 'bg-emerald-50 text-emerald-700 border-emerald-100',
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize border ${map[status] ?? 'bg-slate-50 text-slate-600 border-slate-200'}`}>
      {status}
    </span>
  )
}

export default function AppointmentCard({ appt }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-sm hover:shadow-md transition-shadow duration-300 relative overflow-hidden group">
      <div className="absolute left-0 top-0 w-1 h-full bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
      <div className="flex items-start justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600">
             <Calendar className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-0.5">Date</p>
            <span className="font-semibold text-slate-800">{appt.appointment_date}</span>
          </div>
        </div>
        {statusBadge(appt.status)}
      </div>

      <div className="grid grid-cols-2 gap-4 bg-slate-50 rounded-xl p-4">
        <div className="flex items-center gap-2 text-slate-700 text-sm font-medium">
          <Clock className="w-4 h-4 text-slate-400" />
          <span>{appt.slot}</span>
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
