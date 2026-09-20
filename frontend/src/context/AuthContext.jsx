import { createContext, useContext, useEffect, useState } from 'react'
import { authService } from '../services/services'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!localStorage.getItem('stillroom_token')) {
      setLoading(false)
      return
    }
    authService.me().then(({ data }) => setUser(data)).catch(() => localStorage.removeItem('stillroom_token')).finally(() => setLoading(false))
  }, [])

  async function login(credentials) {
    const { data } = await authService.login(credentials)
    localStorage.setItem('stillroom_token', data.access_token)
    const currentUser = await authService.me()
    setUser(currentUser.data)
    return currentUser.data
  }

  async function register(payload) {
    await authService.register(payload)
    return login({ email: payload.email, password: payload.password })
  }

  function logout() {
    localStorage.removeItem('stillroom_token')
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
