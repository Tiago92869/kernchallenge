import { apiClient } from './apiClient'

export async function loginRequest({ email, password }) {
  const response = await apiClient.post('/auth/login', { email, password })
  return response.data?.data || {}
}

export async function createAccountRequest({ email, firstname, lastname, password }) {
  const response = await apiClient.post('/users', {
    email,
    firstname,
    lastname,
    password,
  })
  return response.data?.data || {}
}

export async function forgotPasswordRequest({ email }) {
  const response = await apiClient.post('/auth/forgot-password', { email })
  return {
    message: response.data?.message || 'A new password was sent to your email',
  }
}

export async function logoutRequest() {
  await apiClient.post('/auth/logout')
}
