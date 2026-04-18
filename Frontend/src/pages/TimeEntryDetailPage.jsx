import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'

import ConfirmDeleteModal from '../components/ConfirmDeleteModal'
import TimeEntryFormModal from '../components/TimeEntryFormModal'
import { useAuth } from '../hooks/useAuth'
import { MOCK_PROJECTS } from '../mocks/timeEntries'
import { getMockTimeEntryById } from '../mocks/timeEntries'

function formatLongDate(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatDuration(durationMinutes) {
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60
  return `${hours}h ${String(minutes).padStart(2, '0')}m`
}

function getProjectInitials(name) {
  return name
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
}

function buildFocusLabel(description) {
  const normalized = (description || '').trim()
  if (!normalized) {
    return 'General work entry'
  }

  const sentence = normalized.split(/[.!?]/)[0].trim()
  if (sentence.length <= 36) {
    return sentence
  }

  return `${sentence.slice(0, 33)}...`
}

function parseUserIdFromToken(token) {
  if (!token) return null

  const parts = token.split('.')
  if (parts.length < 2) return null

  try {
    const payload = JSON.parse(atob(parts[1]))
    return payload?.sub || null
  } catch {
    return null
  }
}

function TimeEntryDetailPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { id } = useParams()
  const { token } = useAuth()
  const currentUserId = useMemo(() => parseUserIdFromToken(token), [token])

  const [entry, setEntry] = useState(() => location.state?.entry || getMockTimeEntryById(id))
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)

  useEffect(() => {
    setEntry(location.state?.entry || getMockTimeEntryById(id))
  }, [id, location.state])

  const isEntryOwner = !entry?.userId || !currentUserId || entry.userId === currentUserId

  if (!entry) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Time entry not found.</p>
          <button type="button" className="btn-primary entry-missing-link" onClick={() => navigate(-1)}>
            Back to Entries
          </button>
        </div>
      </section>
    )
  }

  return (
    <section className="dashboard-stack entry-detail-page">

      <div className="dashboard-card entry-detail-hero">
        <div className="entry-detail-hero-main">
          <span className={`entry-detail-avatar ${entry.project?.accent || 'blue'}`} aria-hidden="true">
            {getProjectInitials(entry.project?.name || 'Project')}
          </span>

          <div className="entry-detail-headline">
            <h2>{entry.project?.name}</h2>
            <p className="muted">{entry.focus}</p>
          </div>
        </div>

        <div className="entry-detail-hero-side">
          <span className={`status-badge ${entry.project?.visibility?.toLowerCase() || 'public'}`}>
            {entry.project?.visibility === 'PRIVATE' ? 'Private project' : 'Public project'}
          </span>
          {isEntryOwner ? (
            <div className="entry-detail-actions">
              <button type="button" className="btn-secondary" onClick={() => setIsEditOpen(true)}>
                Edit Entry
              </button>
              <button type="button" className="btn-danger" onClick={() => setIsDeleteOpen(true)}>
                Delete Entry
              </button>
            </div>
          ) : null}
        </div>
      </div>

      <section className="entry-detail-metrics">
        <article className="dashboard-card entry-metric-card">
          <p className="entries-summary-label">Duration</p>
          <strong>{formatDuration(entry.durationMinutes)}</strong>
          <span className="muted">logged for this work session</span>
        </article>

        <article className="dashboard-card entry-metric-card">
          <p className="entries-summary-label">Work Date</p>
          <strong>{formatLongDate(entry.date)}</strong>
          <span className="muted">ordered from the mocked entries list</span>
        </article>
      </section>

      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>Description</h2>
        </div>
        <p className="entry-detail-description">{entry.description}</p>
      </div>

      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>Entry Overview</h2>
        </div>

        <div className="profile-details-grid">
          <div className="profile-field">
            <label>Project</label>
            <p>{entry.project?.name}</p>
          </div>
          <div className="profile-field">
            <label>Visibility</label>
            <p>{entry.project?.visibility === 'PRIVATE' ? 'Private' : 'Public'}</p>
          </div>
          <div className="profile-field">
            <label>Logged By</label>
            <p>{entry.loggedBy || '-'}</p>
          </div>
          <div className="profile-field">
            <label>Created At</label>
            <p>{entry.createdAt ? formatDateTime(entry.createdAt) : '-'}</p>
          </div>
          <div className="profile-field">
            <label>Last Updated</label>
            <p>{entry.updatedAt ? formatDateTime(entry.updatedAt) : '-'}</p>
          </div>
        </div>
      </div>

      {isEntryOwner ? (
        <>
          <TimeEntryFormModal
            key={`detail-${entry.id}-${isEditOpen ? 'open' : 'closed'}`}
            isOpen={isEditOpen}
            mode="edit"
            entry={entry}
            projects={MOCK_PROJECTS}
            onClose={() => setIsEditOpen(false)}
            onSave={(values) => {
              const nextProject = MOCK_PROJECTS.find((project) => project.id === values.projectId) || null
              setEntry((current) => ({
                ...current,
                projectId: values.projectId,
                project: nextProject,
                date: values.date,
                durationMinutes: values.durationMinutes,
                description: values.description,
                focus: buildFocusLabel(values.description),
                updatedAt: '2026-04-17T12:00:00',
              }))
              setIsEditOpen(false)
            }}
          />

          <ConfirmDeleteModal
            isOpen={isDeleteOpen}
            description={entry.description}
            onCancel={() => setIsDeleteOpen(false)}
            onConfirm={() => navigate('/time-entries')}
          />
        </>
      ) : null}
    </section>
  )
}

export default TimeEntryDetailPage
