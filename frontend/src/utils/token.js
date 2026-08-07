const TOKEN_KEY = 'access_token'
const ROLE_KEY = 'role'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token)
export const removeToken = () => localStorage.removeItem(TOKEN_KEY)

export const getRole = () => localStorage.getItem(ROLE_KEY)
export const setRole = (role) => localStorage.setItem(ROLE_KEY, role)
export const removeRole = () => localStorage.removeItem(ROLE_KEY)

export const clearAuth = () => {
  removeToken()
  removeRole()
}
