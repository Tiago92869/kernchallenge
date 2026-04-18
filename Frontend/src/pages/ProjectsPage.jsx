import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import ProjectCreateModal from '../components/ProjectCreateModal'
import { createProject, getProjects } from '../services/projectService'

function formatCreatedDate(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatLastEntry(dateString) {
  if (!dateString) {
    return 'No entries yet'
  }

  const diffMs = Math.max(0, Date.now() - new Date(dateString).getTime())
  const oneDay = 24 * 60 * 60 * 1000

  if (diffMs < oneDay) {
    return 'Today'
  }

  if (diffMs < oneDay * 2) {
    return 'Yesterday'
  }

  const days = Math.floor(diffMs / oneDay)
  if (days <= 14) {
    return `${days} days ago`
  }

  return formatCreatedDate(dateString)
}

function getMemberInitials(member) {
  return `${member.firstName[0] || ''}${member.lastName[0] || ''}`.toUpperCase()
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

function getUserRoleLabel(project) {
  if (project.is_archived) {
    return 'Archived'
  }

  if (project.user_role === 'OWNER' || project.is_owner) {
    return 'Owner'
  }

  if (project.user_role === 'MEMBER' || project.is_member) {
    return 'Member'
  }

  return 'No role'
}

function normalizeProject(apiProject) {
  return {
    id: apiProject.id,
    name: apiProject.name,
    description: apiProject.description || '',
    visibility: apiProject.visibility,
    is_archived: apiProject.is_archived,
    is_owner: apiProject.is_owner,
    is_member: Boolean(apiProject.is_member),
    user_role: apiProject.user_role || null,
    isMine: apiProject.is_owner,
    canAccess: true,
    created_at: apiProject.created_at,
    createdAt: apiProject.created_at,
    last_entry_at: apiProject.last_entry_at,
    lastEntryAt: apiProject.last_entry_at,
    members: (apiProject.members || []).map((m) => ({
      id: m.id,
      firstName: m.first_name,
      lastName: m.last_name,
      email: m.email,
    })),
  }
}

function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchValue, setSearchValue] = useState('')
  const [isMyProjectsOnly, setIsMyProjectsOnly] = useState(false)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [accessModal, setAccessModal] = useState(null)

  const loadProjects = useCallback(async () => {
    setLoading(true)
    const fetched = await getProjects()
    setProjects(fetched.map(normalizeProject))
    setLoading(false)
  }, [])

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  const visibleProjects = useMemo(() => {
    const normalized = searchValue.trim().toLowerCase()

    return projects
      .filter((project) => {
        if (isMyProjectsOnly && !project.is_owner) {
          return false
        }

        if (!normalized) {
          return true
        }

        return [project.name, project.description, project.visibility, getUserRoleLabel(project)]
          .join(' ')
          .toLowerCase()
          .includes(normalized)
      })
      .sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime())
  }, [projects, searchValue, isMyProjectsOnly])

  async function handleCreateProject(values) {
    const created = await createProject({
      name: values.name,
      description: values.description,
      visibility: values.visibility,
    })

    if (created) {
      setProjects((current) => [normalizeProject(created), ...current])
    }
    setIsCreateOpen(false)
  }

  function handleOpenProject(project) {
    if (project.is_archived) {
      setAccessModal({ type: 'archived', project })
      return
    }

    navigate(`/projects/${project.id}`)
  }

  return (
    <section className="stack-lg projects-list-page">
      <div className={`projects-list-content ${accessModal ? 'blurred' : ''}`}>
        <div className="projects-list-top-actions">
          <button type="button" className="btn-primary" onClick={() => setIsCreateOpen(true)}>
            Create Project
          </button>
        </div>

        <div className="dashboard-card projects-list-filters-card">
          <div className="projects-list-search-row">
            <button type="button" className="notifications-search-btn" aria-label="Search projects">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M15.5 14h-.79l-.28-.27a6 6 0 1 0-.71.71l.27.28v.79L19 20.5 20.5 19zM10 14a4 4 0 1 1 0-8 4 4 0 0 1 0 8z" />
              </svg>
            </button>

            <label className="field projects-list-search-field" htmlFor="project-search-input">
              <span className="sr-only">Search projects</span>
              <input
                id="project-search-input"
                type="search"
                value={searchValue}
                onChange={(event) => setSearchValue(event.target.value)}
                placeholder="Search projects"
              />
            </label>

            <button
              type="button"
              className={`projects-mine-btn${isMyProjectsOnly ? ' active' : ''}`}
              aria-pressed={isMyProjectsOnly}
              onClick={() => setIsMyProjectsOnly((prev) => !prev)}
            >
              {isMyProjectsOnly && (
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
              )}
              My Projects
            </button>
          </div>
        </div>

        <div className="dashboard-card entries-table-card">
          {loading ? (
            <div className="entries-empty-state">
              <p className="muted">Loading projects…</p>
            </div>
          ) : visibleProjects.length ? (
            <div className="entries-table-wrap">
              <table className="entries-table projects-list-table">
                <thead>
                  <tr>
                    <th>Project Name</th>
                    <th>Your Role</th>
                    <th>Members</th>
                    <th>Visibility</th>
                    <th>Created At</th>
                    <th>Last Entry Added</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleProjects.map((project) => {
                    const roleLabel = getUserRoleLabel(project)
                    const roleClass = roleLabel.toLowerCase().replace(/\s+/g, '-')

                    return (
                      <tr
                        key={project.id}
                        className="entries-row-clickable"
                        onClick={() => handleOpenProject(project)}
                      >
                        <td>
                          <div className="project-name-cell">
                            <strong>{project.name}</strong>
                            <p className="muted">
                              {project.members.length} members, Alex
                            </p>
                          </div>
                        </td>

                        <td>
                          <span className={`project-role-badge ${roleClass}`}>{roleLabel}</span>
                        </td>

                        <td>
                          <div className="project-member-bubbles" aria-label={`${project.members.length} members`}>
                            {project.members.slice(0, 3).map((member) => (
                              <span key={member.id} className={`project-member-bubble ${getMemberColorClass(member)}`} title={`${member.firstName} ${member.lastName}`}>
                                {getMemberInitials(member)}
                              </span>
                            ))}
                            {project.members.length > 3 && (
                              <span className="project-member-bubble more">+{project.members.length - 3}</span>
                            )}
                          </div>
                        </td>

                        <td>
                          <span className={`status-badge ${project.visibility.toLowerCase()}`}>
                            {project.visibility === 'PRIVATE' ? 'Private' : 'Public'}
                          </span>
                        </td>

                        <td>{formatCreatedDate(project.createdAt)}</td>
                        <td>{formatLastEntry(project.lastEntryAt)}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="entries-empty-state">
              <h3>No projects match this filter</h3>
              <p className="muted">Try removing the search text or disable My Projects to see all projects.</p>
            </div>
          )}
        </div>
      </div>

      <ProjectCreateModal
        key={isCreateOpen ? 'open-create-project' : 'closed-create-project'}
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSave={handleCreateProject}
      />

      {accessModal ? (
        <div className="modal-overlay" role="presentation" onClick={() => setAccessModal(null)}>
          <article
            className="modal-card private-project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="project-access-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-head private-project-head">
              <span className="private-project-lock" aria-hidden="true">🗄️</span>
              <h2 id="project-access-title">Archived Project</h2>
            </div>

            <div className="modal-body stack-sm private-project-body">
              <p className="confirm-copy">
                <strong>{accessModal?.project?.name}</strong> is archived. Archived projects remain visible for history,
                but no new entries can be added.
              </p>

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setAccessModal(null)}>
                  Close
                </button>
              </div>
            </div>
          </article>
        </div>
      ) : null}
    </section>
  )
}

export default ProjectsPage
