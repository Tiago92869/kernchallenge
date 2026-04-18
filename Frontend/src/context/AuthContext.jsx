import { useCallback, useEffect, useMemo, useState } from 'react'

import { loginRequest, logoutRequest } from '../services/authService'
import { clearAuthTokens, getAccessToken, persistAuthTokens } from '../services/authStorage'
import { AuthContext } from './authContext'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getAccessToken())
  const [isLoading, setIsLoading] = useState(false)

  const isAuthenticated = Boolean(token)

  const login = useCallback(async ({ email, password, rememberMe = true }) => {
    setIsLoading(true)
    try {
      const payload = await loginRequest({ email, password })
      const newToken = payload.auth_token
      if (!newToken) {
        throw new Error('Token missing in login response')
      }

      persistAuthTokens(
        {
          authToken: newToken,
          refreshToken: payload.refresh_token,
        },
        { rememberMe },
      )
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
      clearAuthTokens()
      setToken(null)
    }
  }, [token])

  useEffect(() => {
    const onUnauthorized = () => {
      clearAuthTokens()
      setToken(null)
    }

    const onTokenRefreshed = (event) => {
      const refreshedToken = event?.detail?.token
      if (refreshedToken) {
        setToken(refreshedToken)
      }
    }

    window.addEventListener('auth:unauthorized', onUnauthorized)
    window.addEventListener('auth:token-refreshed', onTokenRefreshed)

    return () => {
      window.removeEventListener('auth:unauthorized', onUnauthorized)
      window.removeEventListener('auth:token-refreshed', onTokenRefreshed)
    }
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
