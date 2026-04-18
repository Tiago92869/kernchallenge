import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import ConfirmDeleteModal from '../components/ConfirmDeleteModal'
import TimeEntryFormModal from '../components/TimeEntryFormModal'
import { createTimeEntry, deleteTimeEntry, getMyProjects, getTimeEntries, updateTimeEntry } from '../services/timeEntryService'

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatDuration(durationMinutes) {
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  if (!hours) {
    return `${minutes}m`
  }

  return `${hours}h ${String(minutes).padStart(2, '0')}m`
}

function formatFilteredHours(durationMinutes) {
  const hours = durationMinutes / 60
  return `${hours.toFixed(1)}h`
}

function getProjectInitials(name) {
  return name
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
}

function matchesDateRange(dateString, fromDate, toDate) {
  if (!fromDate && !toDate) return true
  if (fromDate && dateString < fromDate) return false
  if (toDate && dateString > toDate) return false
  return true
}

// Normalize API entry to internal shape used throughout the page
function normalizeEntry(apiEntry, projectsById) {
  return {
    id: apiEntry.id,
    project_id: apiEntry.project_id,
    date: apiEntry.date,
    durationMinutes: apiEntry.hours, // API field named "hours" contains minutes
    description: apiEntry.description,
    project: projectsById[apiEntry.project_id] || null,
  }
}

function TimeEntriesPage() {
  const navigate = useNavigate()
  const [entries, setEntries] = useState([])
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchValue, setSearchValue] = useState('')
  const [projectFilter, setProjectFilter] = useState('all')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [formState, setFormState] = useState({ mode: null, entry: null })
  const [entryToDelete, setEntryToDelete] = useState(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    const [entriesResult, projectsResult] = await Promise.allSettled([getTimeEntries(), getMyProjects()])

    const fetchedProjects = projectsResult.status === 'fulfilled' ? projectsResult.value : []
    const projectsById = Object.fromEntries(fetchedProjects.map((p) => [p.id, p]))

    setProjects(fetchedProjects)

    if (entriesResult.status === 'fulfilled') {
      setEntries(entriesResult.value.map((entry) => normalizeEntry(entry, projectsById)))
    }

    setLoading(false)
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const filteredEntries = useMemo(() => {
    const normalizedSearch = searchValue.trim().toLowerCase()

    return entries
      .filter((entry) => {
        if (projectFilter !== 'all' && entry.project_id !== projectFilter) {
          return false
        }

        if (!matchesDateRange(entry.date, fromDate, toDate)) {
          return false
        }

        if (!normalizedSearch) {
          return true
        }

        return [entry.description, entry.project?.name || '']
          .join(' ')
          .toLowerCase()
          .includes(normalizedSearch)
      })
      .sort((left, right) => right.date.localeCompare(left.date))
  }, [entries, projectFilter, searchValue, fromDate, toDate])

  const filteredTotals = useMemo(() => {
    const totalMinutes = filteredEntries.reduce((sum, entry) => sum + entry.durationMinutes, 0)
    const uniqueProjects = new Set(filteredEntries.map((entry) => entry.project_id)).size

    return {
      totalEntries: filteredEntries.length,
      totalMinutes,
      uniqueProjects,
    }
  }, [filteredEntries])

  function closeFormModal() {
    setFormState({ mode: null, entry: null })
  }

  async function handleSaveEntry(values) {
    const payload = {
      project_id: values.projectId,
      date: values.date,
      hours: values.durationMinutes,
      description: values.description,
    }

    if (formState.mode === 'edit' && formState.entry) {
      const updated = await updateTimeEntry(formState.entry.id, payload)
      if (updated) {
        const projectsById = Object.fromEntries(projects.map((p) => [p.id, p]))
        setEntries((current) =>
          current.map((entry) =>
            entry.id === formState.entry.id ? normalizeEntry(updated, projectsById) : entry,
          ),
        )
      }
      closeFormModal()
      return
    }

    const created = await createTimeEntry(payload)
    if (created) {
      const projectsById = Object.fromEntries(projects.map((p) => [p.id, p]))
      setEntries((current) => [normalizeEntry(created, projectsById), ...current])
    }
    closeFormModal()
  }

  async function handleDeleteEntry() {
    if (!entryToDelete) return
    await deleteTimeEntry(entryToDelete.id)
    setEntries((current) => current.filter((entry) => entry.id !== entryToDelete.id))
    setEntryToDelete(null)
  }

  return (
    <section className="entries-page stack-lg">
      <div className="dashboard-card entries-filters-card">
        <div className="entries-filters-grid">
          <div className="entries-search-row">
            <button type="button" className="notifications-search-btn" aria-label="Search time entries">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M15.5 14h-.79l-.28-.27a6 6 0 1 0-.71.71l.27.28v.79L19 20.5 20.5 19zM10 14a4 4 0 1 1 0-8 4 4 0 0 1 0 8z" />
              </svg>
            </button>

            <label className="field entries-search-field" htmlFor="entry-search">
              Search entries
              <input
                id="entry-search"
                type="search"
                value={searchValue}
                onChange={(event) => setSearchValue(event.target.value)}
                placeholder="Search by description or project"
              />
            </label>
          </div>

          <label className="field" htmlFor="entry-project-filter">
            Project
            <select
              id="entry-project-filter"
              value={projectFilter}
              onChange={(event) => setProjectFilter(event.target.value)}
            >
              <option value="all">All projects</option>
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="entries-date-range-row">
          <label className="field" htmlFor="entry-from-date">
            From
            <input
              id="entry-from-date"
              type="date"
              value={fromDate}
              max={toDate || undefined}
              onChange={(event) => setFromDate(event.target.value)}
            />
          </label>

          <label className="field" htmlFor="entry-to-date">
            To
            <input
              id="entry-to-date"
              type="date"
              value={toDate}
              min={fromDate || undefined}
              onChange={(event) => setToDate(event.target.value)}
            />
          </label>
        </div>
      </div>

      <section className="entries-summary-strip">
        <article className="entries-summary-card">
          <p className="entries-summary-label">Total Entries</p>
          <strong>{filteredTotals.totalEntries}</strong>
          <span className="muted">matching the current filters</span>
        </article>

        <article className="entries-summary-card">
          <p className="entries-summary-label">Filtered Hours</p>
          <strong>{formatFilteredHours(filteredTotals.totalMinutes)}</strong>
          <span className="muted">across {filteredTotals.uniqueProjects} projects</span>
        </article>
      </section>

      <div className="dashboard-card entries-table-card">
        <div className="dashboard-card-head entries-table-head">
          <h2>Ordered Time Entries</h2>
          <div className="entries-table-head-actions">
            <button type="button" className="btn-primary" onClick={() => setFormState({ mode: 'create', entry: null })}>
              Add Entry
            </button>
          </div>
        </div>

        {loading ? (
          <div className="entries-empty-state">
            <p className="muted">Loading entries…</p>
          </div>
        ) : filteredEntries.length ? (
          <div className="entries-table-wrap">
            <table className="entries-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Project</th>
                  <th>Description</th>
                  <th>Duration</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredEntries.map((entry) => (
                  <tr
                    key={entry.id}
                    className="entries-row-clickable"
                    onClick={() => navigate(`/time-entries/${entry.id}`)}
                  >
                    <td>{formatDate(entry.date)}</td>
                    <td>
                      <div className="entry-project-cell">
                        <span className="entry-project-avatar blue" aria-hidden="true">
                          {getProjectInitials(entry.project?.name || 'P')}
                        </span>
                        <div>
                          <strong>{entry.project?.name ?? 'Unknown project'}</strong>
                          <span className={`status-badge ${entry.project?.visibility?.toLowerCase() || 'public'}`}>
                            {entry.project?.visibility === 'PRIVATE' ? 'Private' : 'Public'}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="entry-description-cell">
                        <p className="muted">{entry.description}</p>
                      </div>
                    </td>
                    <td>{formatDuration(entry.durationMinutes)}</td>
                    <td>
                      <div className="entry-actions">
                        <button
                          type="button"
                          className="icon-action-btn edit"
                          aria-label={`Edit entry on ${formatDate(entry.date)}`}
                          title="Edit entry"
                          onClick={(event) => {
                            event.stopPropagation()
                            setFormState({ mode: 'edit', entry })
                          }}
                        >
                          <svg viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M4 17.25V20h2.75L17.81 8.94l-2.75-2.75z" />
                            <path d="M19.71 7.04a1.003 1.003 0 0 0 0-1.42L18.37 4.29a1.003 1.003 0 0 0-1.42 0l-1.13 1.13 2.75 2.75z" />
                          </svg>
                        </button>
                        <button
                          type="button"
                          className="icon-action-btn delete"
                          aria-label={`Delete entry on ${formatDate(entry.date)}`}
                          title="Delete entry"
                          onClick={(event) => {
                            event.stopPropagation()
                            setEntryToDelete(entry)
                          }}
                        >
                          <svg viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M6 7h12l-1 13H7zm3-3h6l1 2H8z" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="entries-empty-state">
            <h3>No entries match the current filters</h3>
            <p className="muted">Try removing the search text or broadening the selected project and time range.</p>
          </div>
        )}
      </div>

      <TimeEntryFormModal
        key={`${formState.mode || 'closed'}-${formState.entry?.id || 'new'}`}
        isOpen={Boolean(formState.mode)}
        mode={formState.mode}
        entry={formState.entry ? { ...formState.entry, projectId: formState.entry.project_id } : null}
        projects={projects}
        onClose={closeFormModal}
        onSave={handleSaveEntry}
      />

      <ConfirmDeleteModal
        isOpen={Boolean(entryToDelete)}
        description={entryToDelete?.description}
        onCancel={() => setEntryToDelete(null)}
        onConfirm={handleDeleteEntry}
      />
    </section>
  )
}

export default TimeEntriesPage
