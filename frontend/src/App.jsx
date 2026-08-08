import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ToastProvider } from './components/Toast'
import ProtectedRoute from './components/ProtectedRoute'

// Auth pages
import Login from './pages/auth/Login'
import Signup from './pages/auth/Signup'

// Patient pages
import Dashboard from './pages/patient/Dashboard'
import BookAppointment from './pages/patient/BookAppointment'
import MyAppointments from './pages/patient/MyAppointments'
import Schedule from './pages/patient/Schedule'

// Doctor pages
import DoctorDashboard from './pages/doctor/DoctorDashboard'
import DoctorSchedule from './pages/doctor/DoctorSchedule'

// Owner/Admin pages
import OwnerDashboard from './pages/owner/OwnerDashboard'
import SuperadminDashboard from './pages/admin/SuperadminDashboard'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Patient routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute allowedRoles={['patient']}>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/book" element={
              <ProtectedRoute allowedRoles={['patient']}>
                <BookAppointment />
              </ProtectedRoute>
            } />
            <Route path="/my-appointments" element={
              <ProtectedRoute allowedRoles={['patient']}>
                <MyAppointments />
              </ProtectedRoute>
            } />
            <Route path="/schedule" element={
              <ProtectedRoute allowedRoles={['patient']}>
                <Schedule />
              </ProtectedRoute>
            } />

            {/* Doctor routes */}
            <Route path="/doctor/dashboard" element={
              <ProtectedRoute allowedRoles={['doctor']}>
                <DoctorDashboard />
              </ProtectedRoute>
            } />
            <Route path="/doctor/schedule" element={
              <ProtectedRoute allowedRoles={['doctor']}>
                <DoctorSchedule />
              </ProtectedRoute>
            } />

            {/* Owner routes */}
            <Route path="/owner/dashboard" element={
              <ProtectedRoute allowedRoles={['owner']}>
                <OwnerDashboard />
              </ProtectedRoute>
            } />

            {/* Admin routes */}
            <Route path="/admin/dashboard" element={
              <ProtectedRoute allowedRoles={['superadmin']}>
                <SuperadminDashboard />
              </ProtectedRoute>
            } />

            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
