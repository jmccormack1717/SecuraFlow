import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { authApi } from '../services/api'

interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  created_at: string
}

interface AuthContextType {
  user: User | null
  isDemo: boolean
  token: string | null
  login: (username: string, password: string) => Promise<void>
  signup: (email: string, username: string, password: string) => Promise<void>
  demoLogin: () => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('token')
  })
  const [isDemo, setIsDemo] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if we have a token on mount
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      // Try to get user info
      fetchUser(storedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUser = async (authToken: string) => {
    try {
      const userData = await authApi.getCurrentUser(authToken)
      setUser(userData)
      setIsDemo(false)
    } catch (error) {
      // If it's a demo token or invalid, clear it
      console.error('Failed to fetch user:', error)
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const response = await authApi.login(username, password)
    setToken(response.access_token)
    localStorage.setItem('token', response.access_token)
    setIsDemo(false)
    await fetchUser(response.access_token)
  }

  const signup = async (email: string, username: string, password: string) => {
    await authApi.signup(email, username, password)
    // After signup, automatically log in
    await login(username, password)
  }

  const demoLogin = async () => {
    const response = await authApi.demoLogin()
    setToken(response.access_token)
    localStorage.setItem('token', response.access_token)
    setIsDemo(true)
    setUser({
      id: 0,
      email: 'demo@securaflow.com',
      username: 'demo_user',
      is_active: true,
      created_at: new Date().toISOString(),
    })
    setIsLoading(false)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    setIsDemo(false)
    localStorage.removeItem('token')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isDemo,
        token,
        login,
        signup,
        demoLogin,
        logout,
        isLoading,
      }}
    >
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



