import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import ConfirmDeleteModal from '../components/ConfirmDeleteModal'
import ProjectCreateModal from '../components/ProjectCreateModal'
import TimeEntryFormModal from '../components/TimeEntryFormModal'
import { getApiErrorMessage } from '../services/apiError'
import { archiveProject, getProjectDetails, updateProject } from '../services/projectService'
import { createTimeEntry, getProjectTimeEntries } from '../services/timeEntryService'

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  })
}

function formatLongDate(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatDuration(durationMinutes) {
  const hours = durationMinutes / 60
  return `${hours.toFixed(1)} hr`
}

function getInitials(firstName, lastName) {
  return `${firstName[0] || ''}${lastName[0] || ''}`.toUpperCase()
}

function matchesDateRange(dateString, fromDate, toDate) {
  if (!fromDate && !toDate) return true
  if (fromDate && dateString < fromDate) return false
  if (toDate && dateString > toDate) return false
  return true
}

function normalizeProjectDetails(apiProject) {
  const members = Array.isArray(apiProject?.members)
    ? apiProject.members.map((member) => ({
        id: member.id,
        firstName: member.first_name,
        lastName: member.last_name,
        email: member.email,
      }))
    : []

  return {
    id: apiProject.id,
    name: apiProject.name,
    description: apiProject.description,
    visibility: apiProject.visibility,
    isArchived: Boolean(apiProject.is_archived),
    isOwner: Boolean(apiProject.is_owner),
    userRole: apiProject.user_role,
    ownerId: apiProject.owner_id,
    members,
    createdAt: apiProject.created_at,
    lastEntryAt: apiProject.last_entry_at,
  }
}

function normalizeEntries(apiEntries, membersById) {
  return apiEntries.map((entry) => {
    const member = membersById.get(entry.user_id)
    const firstName = member?.firstName || 'Unknown'
    const lastName = member?.lastName || 'User'
    return {
      id: entry.id,
      projectId: entry.project_id,
      userId: entry.user_id,
      date: entry.date,
      durationMinutes: entry.hours,
      description: entry.description,
      loggedBy: `${firstName} ${lastName}`.trim(),
      user: {
        firstName,
        lastName,
      },
    }
  })
}

function ProjectDetailPage() {
  const navigate = useNavigate()
  const { id } = useParams()

  const [project, setProject] = useState(null)
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const [searchValue, setSearchValue] = useState('')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isAddEntryOpen, setIsAddEntryOpen] = useState(false)
  const [isArchiveConfirmOpen, setIsArchiveConfirmOpen] = useState(false)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const projectDetails = await getProjectDetails(id)
      const normalizedProject = normalizeProjectDetails(projectDetails)
      const membersById = new Map(normalizedProject.members.map((member) => [member.id, member]))
      const apiEntries = await getProjectTimeEntries(id)
      const normalizedEntries = normalizeEntries(apiEntries, membersById)

      setProject(normalizedProject)
      setEntries(normalizedEntries)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not load project details.'))
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    loadData()
  }, [loadData])

  const visibleEntries = useMemo(() => {
    const normalized = searchValue.trim().toLowerCase()

    return entries
      .filter((entry) => {
        if (!matchesDateRange(entry.date, fromDate, toDate)) {
          return false
        }

        if (!normalized) {
          return true
        }

        return [entry.user.firstName, entry.user.lastName, entry.description]
          .join(' ')
          .toLowerCase()
          .includes(normalized)
      })
      .sort((left, right) => right.date.localeCompare(left.date))
  }, [entries, searchValue, fromDate, toDate])

  if (loading) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Loading project details...</p>
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

  const isOwner = project.isOwner
  const isArchived = Boolean(project.isArchived)
  const roleLabel = isArchived ? 'Archived' : isOwner ? 'Owner' : 'Member'

  return (
    <section className="stack-lg project-detail-page">
      <div className="blocked-project-content">
        <div className="dashboard-card project-detail-summary-card">
          <div className="project-detail-summary-main">
            <h2>{project.name}</h2>

            <div className="project-detail-meta-row">
              <span className={`status-badge ${project.visibility.toLowerCase()}`}>
                {project.visibility === 'PRIVATE' ? 'Private' : 'Public'}
              </span>
              <span className="project-detail-chip">{project.members.length} members</span>
              <span className="project-detail-chip">{roleLabel}</span>
            </div>
          </div>

          <div className="project-detail-summary-actions">
            {isOwner && !isArchived ? (
              <button type="button" className="btn-secondary" onClick={() => navigate(`/projects/${project.id}/members`)}>
                Manage Users
              </button>
            ) : null}

            {!isArchived ? (
              <button type="button" className="btn-primary" onClick={() => setIsAddEntryOpen(true)}>
                Add Entry
              </button>
            ) : null}

            {isOwner && !isArchived ? (
              <button
                type="button"
                className="icon-action-btn edit"
                aria-label="Edit project"
                title="Edit project"
                onClick={() => setIsEditOpen(true)}
                disabled={saving}
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M4 17.25V20h2.75L17.81 8.94l-2.75-2.75z" />
                  <path d="M19.71 7.04a1.003 1.003 0 0 0 0-1.42L18.37 4.29a1.003 1.003 0 0 0-1.42 0l-1.13 1.13 2.75 2.75z" />
                </svg>
              </button>
            ) : null}

            {isOwner && !isArchived ? (
              <button
                type="button"
                className="icon-action-btn archive"
                aria-label="Archive project"
                title="Archive project"
                onClick={() => setIsArchiveConfirmOpen(true)}
                disabled={saving}
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M20.54 5.23 19.15 3.5H4.85L3.46 5.23A1 1 0 0 0 3.25 6v2a1 1 0 0 0 1 1h.75v9.25a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V9h.75a1 1 0 0 0 1-1V6a1 1 0 0 0-.21-.77ZM5.42 5.5h13.16l.4.5H5.02l.4-.5ZM17 17.75H7V9h10v8.75ZM9.5 11.75h5v1.5h-5z" />
                </svg>
              </button>
            ) : null}
          </div>
        </div>

        <div className="dashboard-card entries-filters-card">
          <div className="entries-filters-grid">
            <label className="field entries-search-field" htmlFor="project-entry-search">
              Search entries
              <input
                id="project-entry-search"
                type="search"
                value={searchValue}
                onChange={(event) => setSearchValue(event.target.value)}
                placeholder="Search by user or description"
              />
            </label>
          </div>

          <div className="entries-date-range-row">
            <label className="field" htmlFor="project-entry-from-date">
              From
              <input
                id="project-entry-from-date"
                type="date"
                value={fromDate}
                max={toDate || undefined}
                onChange={(event) => setFromDate(event.target.value)}
              />
            </label>

            <label className="field" htmlFor="project-entry-to-date">
              To
              <input
                id="project-entry-to-date"
                type="date"
                value={toDate}
                min={fromDate || undefined}
                onChange={(event) => setToDate(event.target.value)}
              />
            </label>
          </div>
        </div>

        <div className="dashboard-card entries-table-card">
          <div className="dashboard-card-head entries-table-head">
            <h2>Entries</h2>
          </div>

          {visibleEntries.length ? (
            <div className="entries-table-wrap">
              <table className="entries-table project-detail-entries-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleEntries.map((entry) => (
                    <tr
                      key={entry.id}
                      className="entries-row-clickable"
                      onClick={() => navigate(`/time-entries/${entry.id}`, { state: { entry } })}
                    >
                      <td>
                        <div className="project-entry-user-cell">
                          <span className="project-member-bubble">{getInitials(entry.user.firstName, entry.user.lastName)}</span>
                          <span>{entry.user.firstName}</span>
                        </div>
                      </td>
                      <td>
                        <div className="project-entry-date-cell">
                          <span>{formatDate(entry.date)}</span>
                          <span className="muted">{formatLongDate(entry.date)}</span>
                        </div>
                      </td>
                      <td>{entry.description}</td>
                      <td>{formatDuration(entry.durationMinutes)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="entries-empty-state">
              <h3>No entries match the current filters</h3>
              <p className="muted">Try changing search text or adjusting the selected date range.</p>
            </div>
          )}
        </div>
      </div>

      <ProjectCreateModal
        key={`edit-project-${project.id}-${isEditOpen ? 'open' : 'closed'}-${project.updatedAt || project.name}`}
        isOpen={isEditOpen}
        mode="edit"
        project={project}
        onClose={() => setIsEditOpen(false)}
        onSave={async (values) => {
          setSaving(true)
          try {
            await updateProject(project.id, values)
            await loadData()
            setIsEditOpen(false)
          } catch (requestError) {
            setError(getApiErrorMessage(requestError, 'Could not update project.'))
          } finally {
            setSaving(false)
          }
        }}
      />

      <TimeEntryFormModal
        key={`project-add-entry-${project.id}-${isAddEntryOpen ? 'open' : 'closed'}`}
        isOpen={isAddEntryOpen}
        mode="create"
        entry={null}
        projects={[{ id: project.id, name: project.name }]}
        lockedProjectId={project.id}
        onClose={() => setIsAddEntryOpen(false)}
        onSave={async (values) => {
          setSaving(true)
          try {
            await createTimeEntry({
              project_id: project.id,
              date: values.date,
              hours: values.durationMinutes,
              description: values.description,
            })
            await loadData()
            setIsAddEntryOpen(false)
          } catch (requestError) {
            setError(getApiErrorMessage(requestError, 'Could not create time entry.'))
          } finally {
            setSaving(false)
          }
        }}
      />

      <ConfirmDeleteModal
        isOpen={isArchiveConfirmOpen}
        onCancel={() => setIsArchiveConfirmOpen(false)}
        onConfirm={async () => {
          setSaving(true)
          try {
            await archiveProject(project.id)
            await loadData()
            setIsArchiveConfirmOpen(false)
          } catch (requestError) {
            setError(getApiErrorMessage(requestError, 'Could not archive project.'))
          } finally {
            setSaving(false)
          }
        }}
        title="Archive Project"
        message="Are you sure you want to archive this project? After this action, you will not be able to go back."
        confirmText="Archive Project"
        cancelText="Cancel"
        confirmClassName="btn-danger"
      />
    </section>
  )
}

export default ProjectDetailPage


