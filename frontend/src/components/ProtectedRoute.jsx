import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, role } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    // Redirect to the correct dashboard based on role
    let fallback = '/dashboard'
    if (role === 'doctor') fallback = '/doctor/dashboard'
    else if (role === 'owner') fallback = '/owner/dashboard'
    else if (role === 'superadmin') fallback = '/admin/dashboard'
    
    return <Navigate to={fallback} replace />
  }

  return children
}
