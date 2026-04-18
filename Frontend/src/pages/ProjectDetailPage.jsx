import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import ConfirmDeleteModal from '../components/ConfirmDeleteModal'
import ProjectCreateModal from '../components/ProjectCreateModal'
import TimeEntryFormModal from '../components/TimeEntryFormModal'
import { getMockEntriesByProjectId, getMockProjectById } from '../mocks/projects'

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

function ProjectDetailPage() {
  const navigate = useNavigate()
  const { id } = useParams()

  const [project, setProject] = useState(() => getMockProjectById(id))
  const [searchValue, setSearchValue] = useState('')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isAddEntryOpen, setIsAddEntryOpen] = useState(false)
  const [isArchiveConfirmOpen, setIsArchiveConfirmOpen] = useState(false)

  const [entries, setEntries] = useState(() => getMockEntriesByProjectId(id).map((entry) => ({ ...entry })))

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

  const isOwner = project.userRole === 'OWNER'
  const isArchived = Boolean(project.isArchived)
  const blockReason = project.canAccess === false ? 'private' : isArchived ? 'archived' : null
  const isBlocked = Boolean(blockReason)
  const roleLabel = isArchived ? 'Archived' : isOwner ? 'Owner' : 'Member'

  return (
    <section className="stack-lg project-detail-page">
      <div className={`blocked-project-content ${isBlocked ? 'blurred' : ''}`}>
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
                    <tr key={entry.id}>
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
        onSave={(values) => {
          setProject((current) => ({
            ...current,
            name: values.name,
            description: values.description,
            visibility: values.visibility,
            updatedAt: new Date().toISOString(),
          }))
          setIsEditOpen(false)
        }}
      />

      <TimeEntryFormModal
        key={`project-add-entry-${project.id}-${isAddEntryOpen ? 'open' : 'closed'}`}
        isOpen={isAddEntryOpen}
        mode="create"
        entry={null}
        projects={[project]}
        lockedProjectId={project.id}
        onClose={() => setIsAddEntryOpen(false)}
        onSave={(values) => {
          const now = new Date().toISOString()
          const nextEntry = {
            id: `pentry-${Date.now()}`,
            projectId: project.id,
            user: { firstName: 'Alex', lastName: 'Johnson' },
            date: values.date,
            durationMinutes: values.durationMinutes,
            description: values.description,
            createdAt: now,
            updatedAt: now,
          }

          setEntries((current) => [nextEntry, ...current])
          setIsAddEntryOpen(false)
        }}
      />

      <ConfirmDeleteModal
        isOpen={isArchiveConfirmOpen}
        onCancel={() => setIsArchiveConfirmOpen(false)}
        onConfirm={() => {
          setProject((current) => ({
            ...current,
            isArchived: true,
            updatedAt: new Date().toISOString(),
          }))
          setIsArchiveConfirmOpen(false)
        }}
        title="Archive Project"
        message="Are you sure you want to archive this project? After this action, you will not be able to go back."
        confirmText="Archive Project"
        cancelText="Cancel"
        confirmClassName="btn-danger"
      />

      {isBlocked ? (
        <div className="modal-overlay" role="presentation" onClick={() => navigate('/projects')}>
          <article
            className="modal-card private-project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="project-access-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-head private-project-head">
              <span className="private-project-lock" aria-hidden="true">{blockReason === 'archived' ? '🗄️' : '🔒'}</span>
              <h2 id="project-access-title">{blockReason === 'archived' ? 'Archived Project' : 'Private Project'}</h2>
            </div>

            <div className="modal-body stack-sm private-project-body">
              {blockReason === 'archived' ? (
                <p className="confirm-copy">
                  <strong>{project.name}</strong> is archived. Archived projects remain visible for history, but no new
                  entries can be added.
                </p>
              ) : (
                <p className="confirm-copy">
                  <strong>{project.name}</strong> is private. You need an invitation from the owner to join.
                </p>
              )}

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => navigate('/projects')}>
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

export default ProjectDetailPage
