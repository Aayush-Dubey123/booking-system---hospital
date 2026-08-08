/**
 * AppointmentCard — reskinned as a CityCare visit-row.
 * Displays a single appointment in a horizontal row layout.
 * All data fields unchanged: appt.reason, appt.symptoms, appt.slot,
 * appt.appointment_date, appt.status.
 */

function getStatusClass(status) {
  if (status === 'booked')     return 'confirmed'
  if (status === 'cancelled')  return 'cancelled'
  if (status === 'completed')  return 'confirmed'
  return 'waiting'
}

function getStatusLabel(status) {
  if (status === 'booked')    return 'Confirmed'
  if (status === 'cancelled') return 'Cancelled'
  if (status === 'completed') return 'Completed'
  return status
}

function getAvatarStyle(index) {
  const styles = [
    { background: 'var(--teal-tint)',  color: 'var(--teal-deep)' },
    { background: 'var(--pulse-tint)', color: 'var(--pulse-deep)' },
    { background: 'var(--amber-tint)', color: 'var(--amber)' },
    { background: 'var(--surface-tint)', color: 'var(--ink-soft)' },
  ]
  return styles[index % styles.length]
}

export default function AppointmentCard({ appt, index = 0 }) {
  const avatarStyle = getAvatarStyle(index)
  // Build initials from date as a visual fallback (patient has no doctor name here)
  const dateStr = appt.appointment_date ? String(appt.appointment_date) : ''
  const initials = dateStr.slice(5, 7) + dateStr.slice(8, 10) // MMDD

  return (
    <div className="visit-row">
      <div className="visit-avatar" style={avatarStyle}>
        {initials}
      </div>
      <div className="visit-info">
        <p className="n">{appt.reason}</p>
        <p className="r">{appt.symptoms}</p>
      </div>
      <div className="visit-time">
        {appt.appointment_date} · {appt.slot}
      </div>
      <div className={`visit-status ${getStatusClass(appt.status)}`}>
        {getStatusLabel(appt.status)}
      </div>
    </div>
  )
}
