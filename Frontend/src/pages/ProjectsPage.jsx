import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import ProjectCreateModal from '../components/ProjectCreateModal'
import { MOCK_PROJECTS } from '../mocks/projects'

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

function getUserRoleLabel(project) {
  if (project.isArchived) {
    return 'Archived'
  }

  if (project.userRole === 'NONE') {
    return 'Not Member'
  }

  return project.userRole === 'OWNER' ? 'Owner' : 'Member'
}

function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState(() => MOCK_PROJECTS.map((project) => ({ ...project })))
  const [searchValue, setSearchValue] = useState('')
  const [isMyProjectsOnly, setIsMyProjectsOnly] = useState(false)
  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [accessModal, setAccessModal] = useState(null)

  const visibleProjects = useMemo(() => {
    const normalized = searchValue.trim().toLowerCase()

    return projects
      .filter((project) => {
        if (isMyProjectsOnly && !project.isMine) {
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
      .sort((left, right) => new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime())
  }, [projects, searchValue, isMyProjectsOnly])

  function handleCreateProject(values) {
    const now = new Date().toISOString()

    const nextProject = {
      id: `project-${Date.now()}`,
      name: values.name,
      description: values.description,
      visibility: values.visibility,
      isArchived: false,
      userRole: 'OWNER',
      isMine: true,
      canAccess: true,
      members: [{ id: 'u-alex', firstName: 'Alex', lastName: 'Johnson' }],
      createdAt: now,
      lastEntryAt: null,
    }

    setProjects((current) => [nextProject, ...current])
    setIsCreateOpen(false)
  }

  function handleOpenProject(project) {
    if (project.isArchived) {
      setAccessModal({ type: 'archived', project })
      return
    }

    if (project.canAccess === false) {
      setAccessModal({ type: 'private', project })
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

            <label className="projects-list-toggle" htmlFor="projects-mine-toggle">
              <input
                id="projects-mine-toggle"
                type="checkbox"
                checked={isMyProjectsOnly}
                onChange={(event) => setIsMyProjectsOnly(event.target.checked)}
              />
              <span>My Projects</span>
            </label>
          </div>
        </div>

        <div className="dashboard-card entries-table-card">
          {visibleProjects.length ? (
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
                              <span key={member.id} className="project-member-bubble" title={`${member.firstName} ${member.lastName}`}>
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
              <p className="muted">Try removing the search text or disable My Projects to see all mocked projects.</p>
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
              <span className="private-project-lock" aria-hidden="true">
                {accessModal.type === 'archived' ? '🗄️' : '🔒'}
              </span>
              <h2 id="project-access-title">{accessModal.type === 'archived' ? 'Archived Project' : 'Private Project'}</h2>
            </div>

            <div className="modal-body stack-sm private-project-body">
              {accessModal.type === 'archived' ? (
                <p className="confirm-copy">
                  <strong>{accessModal.project.name}</strong> is archived. Archived projects remain visible for history,
                  but no new entries can be added.
                </p>
              ) : (
                <p className="confirm-copy">
                  <strong>{accessModal.project.name}</strong> is private. You need an invitation from the owner to join.
                </p>
              )}

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
