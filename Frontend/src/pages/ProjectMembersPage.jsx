import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import AddProjectPeopleModal from '../components/AddProjectPeopleModal'
import { getApiErrorMessage } from '../services/apiError'
import {
  addProjectMembers,
  getProjectDetails,
  getUsers,
  removeProjectMember,
} from '../services/projectService'

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function getInitials(firstName, lastName) {
  return `${firstName[0] || ''}${lastName[0] || ''}`.toUpperCase()
}

function getMemberColorClass(member) {
  const colors = ['color-1', 'color-2', 'color-3', 'color-4', 'color-5', 'color-6']
  let hash = 0
  const str = member.id || member.email || ''
  for (let i = 0; i < str.length; i += 1) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i)
    hash = hash & hash
  }
  const index = Math.abs(hash) % colors.length
  return `project-member-bubble-${colors[index]}`
}

function normalizeProjectDetails(apiProject) {
  const members = Array.isArray(apiProject?.members)
    ? apiProject.members.map((member) => ({
        id: member.id,
        firstName: member.first_name,
        lastName: member.last_name,
        email: member.email,
        joinedAt: apiProject.created_at,
        role: member.id === apiProject.owner_id ? 'OWNER' : 'MEMBER',
      }))
    : []

  return {
    id: apiProject.id,
    name: apiProject.name,
    ownerId: apiProject.owner_id,
    isOwner: Boolean(apiProject.is_owner),
    members,
  }
}

function normalizeUsers(users) {
  return users.map((user) => ({
    id: user.id,
    firstName: user.firstname,
    lastName: user.lastname,
    email: user.email,
    isActive: Boolean(user.is_active),
  }))
}

function ProjectMembersPage() {
  const navigate = useNavigate()
  const { id } = useParams()

  const [project, setProject] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [saving, setSaving] = useState(false)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const [projectDetails, allUsers] = await Promise.all([
        getProjectDetails(id),
        getUsers({ is_active: 'true' }),
      ])

      setProject(normalizeProjectDetails(projectDetails))
      setUsers(normalizeUsers(allUsers))
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not load project members.'))
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    loadData()
  }, [loadData])

  const members = useMemo(() => project?.members ?? [], [project])

  const addableUsers = useMemo(() => {
    const currentIds = new Set(members.map((member) => member.id))
    return users.filter((user) => !currentIds.has(user.id))
  }, [members, users])

  if (loading) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Loading project members...</p>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card stack-sm">
          <p className="muted">{error}</p>
          <button type="button" className="btn-primary" onClick={loadData}>
            Retry
          </button>
        </div>
      </section>
    )
  }

  if (!project) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Project not found.</p>
          <button type="button" className="btn-primary entry-missing-link" onClick={() => navigate('/projects')}>
            Back to Projects
          </button>
        </div>
      </section>
    )
  }

  if (!project.isOwner) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Only project owners can manage members.</p>
          <button type="button" className="btn-primary entry-missing-link" onClick={() => navigate(`/projects/${project.id}`)}>
            Back to Project
          </button>
        </div>
      </section>
    )
  }

  return (
    <>
      <section className={`stack-lg project-members-page ${isAddOpen ? 'blurred' : ''}`}>
        <div className="dashboard-card project-members-header-card">
          <div>
            <h2>{project.name}</h2>
            <p className="project-members-breadcrumb">Project Members</p>
          </div>

          <button type="button" className="btn-primary" onClick={() => setIsAddOpen(true)} disabled={saving}>
            Add People
          </button>
        </div>

        <div className="dashboard-card entries-table-card">
          <div className="entries-table-wrap">
            <table className="entries-table project-members-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Joined At</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {members.map((member) => (
                  <tr key={member.id}>
                    <td>
                      <div className="project-member-name-cell">
                        <span className={`project-member-bubble ${getMemberColorClass(member)}`}>{getInitials(member.firstName, member.lastName)}</span>
                        <strong>{`${member.firstName} ${member.lastName}`}</strong>
                      </div>
                    </td>
                    <td>{member.email}</td>
                    <td>
                      <span className={`project-role-badge ${member.role === 'OWNER' ? 'owner' : 'member'}`}>
                        {member.role === 'OWNER' ? 'Owner' : 'Member'}
                      </span>
                    </td>
                    <td>{formatDate(member.joinedAt)}</td>
                    <td>
                      {member.role === 'OWNER' ? (
                        <span className="muted">-</span>
                      ) : (
                        <button
                          type="button"
                          className="member-remove-btn"
                          disabled={saving}
                          onClick={async () => {
                            setSaving(true)
                            try {
                              await removeProjectMember(project.id, member.id)
                              await loadData()
                            } catch (requestError) {
                              setError(
                                getApiErrorMessage(requestError, 'Could not remove project member.'),
                              )
                            } finally {
                              setSaving(false)
                            }
                          }}
                        >
                          Remove
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <AddProjectPeopleModal
        key={isAddOpen ? 'add-open' : 'add-closed'}
        isOpen={isAddOpen}
        users={addableUsers}
        onClose={() => setIsAddOpen(false)}
        onDone={async (selectedIds) => {
          if (!selectedIds.length) {
            setIsAddOpen(false)
            return
          }

          setSaving(true)
          try {
            await addProjectMembers(project.id, selectedIds)
            await loadData()
            setIsAddOpen(false)
          } catch (requestError) {
            setError(getApiErrorMessage(requestError, 'Could not add project members.'))
          } finally {
            setSaving(false)
          }
        }}
      />
    </>
  )
}

export default ProjectMembersPage


