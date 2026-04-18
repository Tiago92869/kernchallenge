import axios from 'axios'
import { getAccessToken, getRefreshToken, setAccessToken } from './authStorage'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

let refreshPromise = null

function notifyUnauthorized() {
  window.dispatchEvent(new CustomEvent('auth:unauthorized'))
}

function notifyTokenRefreshed(token) {
  window.dispatchEvent(new CustomEvent('auth:token-refreshed', { detail: { token } }))
}

async function refreshAccessToken() {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    throw new Error('Missing refresh token')
  }

  const response = await refreshClient.post('/auth/refresh', null, {
    headers: {
      Authorization: `Bearer ${refreshToken}`,
    },
  })

  const newAccessToken = response.data?.data?.auth_token
  if (!newAccessToken) {
    throw new Error('Token missing in refresh response')
  }

  setAccessToken(newAccessToken)
  notifyTokenRefreshed(newAccessToken)
  return newAccessToken
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config || {}
    const status = error?.response?.status
    const requestUrl = originalRequest?.url || ''

    if (status !== 401) {
      return Promise.reject(error)
    }

    if (
      requestUrl.includes('/auth/login') ||
      requestUrl.includes('/auth/refresh') ||
      originalRequest._retry
    ) {
      notifyUnauthorized()
      return Promise.reject(error)
    }

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null
        })
      }

      const newAccessToken = await refreshPromise
      originalRequest._retry = true
      originalRequest.headers = {
        ...(originalRequest.headers || {}),
        Authorization: `Bearer ${newAccessToken}`,
      }

      return apiClient(originalRequest)
    } catch {
      notifyUnauthorized()
      return Promise.reject(error)
    }
  },
)
