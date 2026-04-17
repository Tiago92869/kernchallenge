import { apiClient } from './apiClient'

function unwrapData(response) {
  return response?.data?.data ?? response?.data ?? null
}

export async function getTimeSummary(params = {}) {
  const response = await apiClient.get('/time-entries/summary', { params })
  return unwrapData(response)
}

export async function getDashboardActivity(period) {
  const response = await apiClient.get('/time-entries/dashboard/activity', {
    params: { period },
  })
  return unwrapData(response)
}

export async function getDashboardPreviewEntries() {
  const response = await apiClient.get('/time-entries/dashboard/preview')
  return unwrapData(response)
}

export async function getDashboardProjectActivity() {
  const response = await apiClient.get('/projects/dashboard/activity')
  return unwrapData(response)
}

export async function getNotificationsPreview(limit = 3) {
  const response = await apiClient.get('/notifications')
  const items = unwrapData(response)
  if (!Array.isArray(items)) {
    return []
  }
  return items.slice(0, limit)
}

export async function getTimeEntriesList(params = {}) {
  const response = await apiClient.get('/time-entries', { params })
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}

export async function getProjectsList(params = {}) {
  const response = await apiClient.get('/projects', { params })
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}
