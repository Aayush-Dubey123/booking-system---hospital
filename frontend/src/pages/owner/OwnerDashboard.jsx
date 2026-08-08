import { useState, useEffect } from 'react'
import { getHospitalDoctors, getHospitalAppointments, addDoctorToHospital } from '../../api/hospitalApi'
import { useAuth } from '../../context/AuthContext'
import Layout from '../../components/Layout'
import PulseDivider from '../../components/PulseDivider'
import { useToast } from '../../components/Toast'
import { Users, Calendar, Plus, Loader2 } from 'lucide-react'

export default function OwnerDashboard() {
  const { hospitalId } = useAuth()
  const [doctors, setDoctors] = useState([])
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  // Add doctor form state
  const [isAdding, setIsAdding] = useState(false)
  const [newDoctor, setNewDoctor] = useState({ first_name: '', last_name: '', email: '', password: '' })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (hospitalId) {
      fetchData()
    } else {
      setLoading(false)
    }
  }, [hospitalId])

  const fetchData = async () => {
    try {
      const [docRes, apptRes] = await Promise.all([
        getHospitalDoctors(hospitalId),
        getHospitalAppointments(hospitalId)
      ])
      setDoctors(docRes.data)
      setAppointments(apptRes.data)
    } catch (err) {
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleAddDoctor = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await addDoctorToHospital(hospitalId, newDoctor)
      toast.success('Doctor added successfully')
      setIsAdding(false)
      setNewDoctor({ first_name: '', last_name: '', email: '', password: '' })
      fetchData() // Refresh list
    } catch (err) {
      toast.error(err.response?.data?.detail ?? 'Failed to add doctor')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <Layout title="Dashboard">
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <Loader2 className="animate-spin" />
        </div>
      </Layout>
    )
  }

  if (!hospitalId) {
    return (
      <Layout title="Dashboard">
        <div className="page-head">
          <div>
            <h1>Dashboard</h1>
            <p>No hospital associated with your account.</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Dashboard">
      <div className="page-head" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Hospital Overview</h1>
          <p>Manage your hospital's doctors and view appointments.</p>
        </div>
        <button className="btn-cc-primary" onClick={() => setIsAdding(!isAdding)}>
          <Plus size={18} />
          {isAdding ? 'Cancel' : 'Add Doctor'}
        </button>
      </div>

      <PulseDivider animKey="owner" />

      {isAdding && (
        <div className="panel" style={{ marginBottom: 24 }}>
          <div className="panel-head">
            <div className="t">
              <Users size={18} />
              <h2>Add New Doctor</h2>
            </div>
          </div>
          <div className="panel-body">
            <form onSubmit={handleAddDoctor} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div className="cc-field">
                <label>First Name</label>
                <input required value={newDoctor.first_name} onChange={e => setNewDoctor({...newDoctor, first_name: e.target.value})} />
              </div>
              <div className="cc-field">
                <label>Last Name</label>
                <input required value={newDoctor.last_name} onChange={e => setNewDoctor({...newDoctor, last_name: e.target.value})} />
              </div>
              <div className="cc-field">
                <label>Email</label>
                <input type="email" required value={newDoctor.email} onChange={e => setNewDoctor({...newDoctor, email: e.target.value})} />
              </div>
              <div className="cc-field">
                <label>Password</label>
                <input type="password" required minLength={8} value={newDoctor.password} onChange={e => setNewDoctor({...newDoctor, password: e.target.value})} />
              </div>
              <div style={{ gridColumn: '1 / -1', marginTop: 16 }}>
                <button type="submit" disabled={submitting} className="btn-cc-primary">
                  {submitting ? 'Adding...' : 'Save Doctor'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'start' }}>
        <div className="panel">
          <div className="panel-head">
            <div className="t">
              <Users size={18} />
              <h2>Doctors ({doctors.length})</h2>
            </div>
          </div>
          <div className="panel-body">
            {doctors.length === 0 ? (
              <p style={{ color: 'var(--ink-soft)' }}>No doctors found.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
                {doctors.map(d => (
                  <li key={d.id} style={{ padding: 12, border: '1px solid var(--line)', borderRadius: 8 }}>
                    <div style={{ fontWeight: 500, color: 'var(--ink)' }}>Dr. {d.first_name} {d.last_name}</div>
                    <div style={{ fontSize: 13, color: 'var(--ink-soft)' }}>{d.email}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-head">
            <div className="t">
              <Calendar size={18} />
              <h2>All Appointments</h2>
            </div>
          </div>
          <div className="panel-body">
            {appointments.length === 0 ? (
              <p style={{ color: 'var(--ink-soft)' }}>No appointments found.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
                {appointments.map(a => (
                  <li key={a.id} style={{ padding: 12, border: '1px solid var(--line)', borderRadius: 8 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ fontWeight: 500, color: 'var(--ink)' }}>{a.appointment_date} at {a.slot}</span>
                      <span className={`status-badge ${a.status}`}>{a.status}</span>
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--ink-soft)', marginTop: 4 }}>
                      Patient: {a.patient_name} <br/>
                      Doctor: {a.doctor_name || 'Pending Assignment'}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
