import { useCallback, useEffect, useMemo, useState } from 'react'

import { loginRequest, logoutRequest } from '../services/authService'
import { AuthContext } from './authContext'

const TOKEN_KEY = 'auth_token'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [isLoading, setIsLoading] = useState(false)

  const isAuthenticated = Boolean(token)

  const login = useCallback(async ({ email, password }) => {
    setIsLoading(true)
    try {
      const payload = await loginRequest({ email, password })
      const newToken = payload.auth_token
      if (!newToken) {
        throw new Error('Token missing in login response')
      }
      localStorage.setItem(TOKEN_KEY, newToken)
      setToken(newToken)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      if (token && token !== 'dev-bypass-token') {
        await logoutRequest()
      }
    } catch {
      // keep logout robust even when token is already invalid
    } finally {
      localStorage.removeItem(TOKEN_KEY)
      setToken(null)
    }
  }, [token])

  useEffect(() => {
    const onUnauthorized = () => {
      localStorage.removeItem(TOKEN_KEY)
      setToken(null)
    }

    window.addEventListener('auth:unauthorized', onUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', onUnauthorized)
  }, [])

  const value = useMemo(
    () => ({
      token,
      isAuthenticated,
      isLoading,
      login,
      logout,
    }),
    [token, isAuthenticated, isLoading, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
