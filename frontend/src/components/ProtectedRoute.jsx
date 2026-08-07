import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, role } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && !allowedRoles.includes(role)) {
    // Redirect to the correct dashboard based on role
    const fallback = role === 'doctor' ? '/doctor/dashboard' : '/dashboard'
    return <Navigate to={fallback} replace />
  }

  return children
}
