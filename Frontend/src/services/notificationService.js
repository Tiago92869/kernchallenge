import { apiClient } from './apiClient'

function unwrapData(response) {
  return response?.data?.data ?? response?.data ?? null
}

export async function getNotifications(params = {}) {
  const response = await apiClient.get('/notifications', { params })
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}

export async function markNotificationRead(id) {
  const response = await apiClient.patch(`/notifications/${id}/read`)
  return unwrapData(response)
}

export async function markAllNotificationsRead() {
  await apiClient.patch('/notifications/read-all')
}
