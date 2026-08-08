import { useState, useEffect } from 'react'
import { getHospitals, createHospital } from '../../api/hospitalApi'
import { getAllOwners, deleteUser } from '../../api/adminApi'
import Layout from '../../components/Layout'
import PulseDivider from '../../components/PulseDivider'
import { useToast } from '../../components/Toast'
import { Building2, Plus, Loader2, Users } from 'lucide-react'

export default function SuperadminDashboard() {
  const [hospitals, setHospitals] = useState([])
  const [owners, setOwners] = useState([])
  const [loading, setLoading] = useState(true)
  const toast = useToast()

  // Create hospital form state
  const [isCreating, setIsCreating] = useState(false)
  const [newHospital, setNewHospital] = useState({ name: '', address: '', phone: '' })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [hospRes, ownersRes] = await Promise.all([
        getHospitals(),
        getAllOwners()
      ])
      setHospitals(hospRes.data)
      setOwners(ownersRes.data)
    } catch (err) {
      toast.error('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateHospital = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await createHospital(newHospital)
      toast.success('Hospital created successfully')
      setIsCreating(false)
      setNewHospital({ name: '', address: '', phone: '' })
      fetchData() // Refresh lists
    } catch (err) {
      toast.error(err.response?.data?.detail ?? 'Failed to create hospital')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <Layout title="Platform Admin">
        <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
          <Loader2 className="animate-spin" />
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="Platform Admin">
      <div className="page-head" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Platform Admin</h1>
          <p>Manage all hospitals and owners on the platform.</p>
        </div>
        <button className="btn-cc-primary" onClick={() => setIsCreating(!isCreating)}>
          <Plus size={18} />
          {isCreating ? 'Cancel' : 'Create Hospital'}
        </button>
      </div>

      <PulseDivider animKey="admin" />

      {isCreating && (
        <div className="panel" style={{ marginBottom: 24 }}>
          <div className="panel-head">
            <div className="t">
              <Building2 size={18} />
              <h2>New Hospital & Owner</h2>
            </div>
          </div>
          <div className="panel-body">
            <form onSubmit={handleCreateHospital} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <h3 style={{ gridColumn: '1 / -1', margin: '0 0 -8px', fontSize: 16 }}>Hospital Details</h3>
              <div className="cc-field" style={{ gridColumn: '1 / -1' }}>
                <label>Hospital Name</label>
                <input required value={newHospital.name} onChange={e => setNewHospital({...newHospital, name: e.target.value})} />
              </div>
              <div className="cc-field" style={{ gridColumn: '1 / -1' }}>
                <label>Address</label>
                <input required value={newHospital.address} onChange={e => setNewHospital({...newHospital, address: e.target.value})} />
              </div>
              <div className="cc-field" style={{ gridColumn: '1 / -1' }}>
                <label>Phone Number</label>
                <input required value={newHospital.phone} onChange={e => setNewHospital({...newHospital, phone: e.target.value})} />
              </div>

              <h3 style={{ gridColumn: '1 / -1', margin: '16px 0 -8px', fontSize: 16, borderTop: '1px solid var(--line)', paddingTop: 16 }}>Owner Details</h3>
              <div className="cc-field">
                <label>Owner First Name</label>
                <input required value={newHospital.owner_first_name || ''} onChange={e => setNewHospital({...newHospital, owner_first_name: e.target.value})} />
              </div>
              <div className="cc-field">
                <label>Owner Last Name</label>
                <input required value={newHospital.owner_last_name || ''} onChange={e => setNewHospital({...newHospital, owner_last_name: e.target.value})} />
              </div>
              <div className="cc-field">
                <label>Owner Email</label>
                <input type="email" required value={newHospital.owner_email || ''} onChange={e => setNewHospital({...newHospital, owner_email: e.target.value})} />
              </div>
              <div className="cc-field">
                <label>Owner Temporary Password</label>
                <input type="password" required minLength={8} value={newHospital.owner_password || ''} onChange={e => setNewHospital({...newHospital, owner_password: e.target.value})} />
              </div>

              <div style={{ gridColumn: '1 / -1', marginTop: 16 }}>
                <button type="submit" disabled={submitting} className="btn-cc-primary">
                  {submitting ? 'Creating...' : 'Create Hospital & Owner'}
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
              <Building2 size={18} />
              <h2>All Hospitals ({hospitals.length})</h2>
            </div>
          </div>
          <div className="panel-body">
            {hospitals.length === 0 ? (
              <p style={{ color: 'var(--ink-soft)' }}>No hospitals registered yet.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
                {hospitals.map(h => (
                  <li key={h.id} style={{ padding: 12, border: '1px solid var(--line)', borderRadius: 8 }}>
                    <div style={{ fontWeight: 500, color: 'var(--ink)' }}>{h.name}</div>
                    <div style={{ fontSize: 13, color: 'var(--ink-soft)' }}>{h.address} • {h.phone}</div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-head">
            <div className="t">
              <Users size={18} />
              <h2>All Owners ({owners.length})</h2>
            </div>
          </div>
          <div className="panel-body">
            {owners.length === 0 ? (
              <p style={{ color: 'var(--ink-soft)' }}>No owners registered yet.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 12 }}>
                {owners.map(o => (
                  <li key={o.id} style={{ padding: 12, border: '1px solid var(--line)', borderRadius: 8 }}>
                    <div style={{ fontWeight: 500, color: 'var(--ink)' }}>{o.first_name} {o.last_name}</div>
                    <div style={{ fontSize: 13, color: 'var(--ink-soft)' }}>
                      {o.email} <br />
                      Hospital: {o.hospital_name || 'None'}
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
