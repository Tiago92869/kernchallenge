import { apiClient } from './apiClient'

export async function loginRequest({ email, password }) {
  const response = await apiClient.post('/auth/login', { email, password })
  return response.data?.data || {}
}

export async function logoutRequest() {
  await apiClient.post('/auth/logout')
}
