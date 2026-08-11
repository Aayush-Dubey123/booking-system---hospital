import { FileText, Download } from 'lucide-react'

function getStatusClass(status) {
  if (status === 'accepted')   return 'confirmed'
  if (status === 'booked')     return 'confirmed'
  if (status === 'cancelled')  return 'cancelled'
  if (status === 'completed')  return 'confirmed'
  return 'waiting'
}

function getStatusLabel(status) {
  if (status === 'accepted')  return 'Accepted'
  if (status === 'pending')   return 'Pending Doctor'
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
  const dateStr = appt.appointment_date ? String(appt.appointment_date) : ''
  const initials = dateStr.slice(5, 7) + dateStr.slice(8, 10)

  return (
    <div className="visit-row" style={{ flexDirection: 'column', alignItems: 'stretch', gap: 12, padding: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="visit-avatar" style={avatarStyle}>
            {initials}
          </div>
          <div className="visit-info">
            <p className="n" style={{ margin: 0, fontWeight: 600 }}>{appt.reason}</p>
            <p className="r" style={{ margin: 0, fontSize: 13, color: 'var(--ink-soft)' }}>
              Doctor: <strong>{appt.doctor_name || 'Pending Assignment'}</strong>
            </p>
          </div>
        </div>
        <div className={`visit-status ${getStatusClass(appt.status)}`}>
          {getStatusLabel(appt.status)}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--line)', paddingTop: 10, fontSize: 13, color: 'var(--ink-soft)' }}>
        <div>
          {appt.hospital_name ? `${appt.hospital_name} · ` : ''}{appt.appointment_date} at {appt.slot}
        </div>

        {appt.prescription?.pdf_url && (
          <a
            href={appt.prescription.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '6px 12px',
              borderRadius: 6,
              background: 'var(--teal-tint)',
              color: 'var(--teal-deep)',
              fontWeight: 500,
              textDecoration: 'none',
              fontSize: 13
            }}
          >
            <FileText size={15} />
            View Prescription PDF
          </a>
        )}
      </div>
    </div>
  )
}
