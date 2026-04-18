import { apiClient } from './apiClient'

function unwrapData(response) {
  return response?.data?.data ?? response?.data ?? null
}

export async function getTimeEntries(params = {}) {
  const response = await apiClient.get('/time-entries', { params })
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}

export async function getProjectTimeEntries(projectId, params = {}) {
  const response = await apiClient.get(`/time-entries/project/${projectId}`, { params })
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}

export async function getMyProjects() {
  const response = await apiClient.get('/projects')
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}

export async function createTimeEntry(data) {
  const response = await apiClient.post('/time-entries', data)
  return unwrapData(response)
}

export async function updateTimeEntry(id, data) {
  const response = await apiClient.put(`/time-entries/${id}`, data)
  return unwrapData(response)
}

export async function deleteTimeEntry(id) {
  await apiClient.delete(`/time-entries/${id}`)
}
