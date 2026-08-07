import { createContext, useState, useCallback } from 'react'
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

  const isAuthenticated = !!token

  const login = useCallback(async (credentials) => {
    const res = await loginApi(credentials)
    const { access_token, role: userRole } = res.data
    setToken(access_token)
    setRole(userRole)
    setTokenState(access_token)
    setRoleState(userRole)
    return userRole
  }, [])

  const signup = useCallback(async (data) => {
    const res = await signupApi(data)
    return res.data
  }, [])

  const logout = useCallback(() => {
    clearAuth()
    setTokenState(null)
    setRoleState(null)
  }, [])

  return (
    <AuthContext.Provider value={{ token, role, isAuthenticated, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
