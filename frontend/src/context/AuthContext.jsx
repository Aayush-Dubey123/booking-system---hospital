import { createContext, useState, useCallback, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as loginApi, signup as signupApi } from '../api/authApi'
import {
  getToken, setToken, removeToken,
  getRole, setRole, removeRole,
  clearAuth,
} from '../utils/token'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(getToken())
  const [role, setRoleState] = useState(getRole())
  const [hospitalId, setHospitalIdState] = useState(localStorage.getItem('hospitalId'))

  const isAuthenticated = !!token

  const login = useCallback(async (credentials) => {
    const res = await loginApi(credentials)
    const { access_token, role: userRole, hospital_id } = res.data
    setToken(access_token)
    setRole(userRole)
    if (hospital_id) localStorage.setItem('hospitalId', hospital_id)
    
    setTokenState(access_token)
    setRoleState(userRole)
    setHospitalIdState(hospital_id || null)
    return { role: userRole, hospitalId: hospital_id }
  }, [])

  const signup = useCallback(async (data) => {
    const res = await signupApi(data)
    return res.data
  }, [])

  const logout = useCallback(() => {
    clearAuth()
    localStorage.removeItem('hospitalId')
    setTokenState(null)
    setRoleState(null)
    setHospitalIdState(null)
  }, [])

  return (
    <AuthContext.Provider value={{ token, role, hospitalId, isAuthenticated, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
