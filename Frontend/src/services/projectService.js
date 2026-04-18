import { apiClient } from './apiClient'

function unwrapData(response) {
  return response?.data?.data ?? response?.data ?? null
}

export async function getProjects(params = {}) {
  const response = await apiClient.get('/projects', { params })
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}

export async function createProject(data) {
  const response = await apiClient.post('/projects', data)
  return unwrapData(response)
}

export async function getProjectDetails(projectId) {
  const response = await apiClient.get(`/projects/${projectId}`)
  return unwrapData(response)
}

export async function updateProject(projectId, data) {
  const response = await apiClient.put(`/projects/${projectId}`, data)
  return unwrapData(response)
}

export async function archiveProject(projectId) {
  const response = await apiClient.patch(`/projects/${projectId}/archive`, { action: 'archive' })
  return unwrapData(response)
}

export async function getProjectMembers(projectId) {
  const response = await apiClient.get(`/project-members/${projectId}/active`)
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}

export async function addProjectMembers(projectId, userIds) {
  const response = await apiClient.put(`/project-members/${projectId}/add`, {
    users_ids: userIds,
  })
  return unwrapData(response)
}

export async function removeProjectMember(projectId, userId) {
  const response = await apiClient.put(`/project-members/${projectId}/${userId}/remove`)
  return unwrapData(response)
}

export async function getUsers(params = {}) {
  const response = await apiClient.get('/users', { params })
  const items = unwrapData(response)
  return Array.isArray(items) ? items : []
}
