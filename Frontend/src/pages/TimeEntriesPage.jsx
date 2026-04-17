import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import ConfirmDeleteModal from '../components/ConfirmDeleteModal'
import TimeEntryFormModal from '../components/TimeEntryFormModal'
import { MOCK_PROJECTS, MOCK_TIME_ENTRIES, getMockProjectById } from '../mocks/timeEntries'

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

function matchesDateRange(dateString, fromDate, toDate) {
  if (!fromDate && !toDate) return true
  if (fromDate && dateString < fromDate) return false
  if (toDate && dateString > toDate) return false
  return true
}

function TimeEntriesPage() {
  const navigate = useNavigate()
  const [entries, setEntries] = useState(() => MOCK_TIME_ENTRIES.map((entry) => ({ ...entry })))
  const [searchValue, setSearchValue] = useState('')
  const [projectFilter, setProjectFilter] = useState('all')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [formState, setFormState] = useState({ mode: null, entry: null })
  const [entryToDelete, setEntryToDelete] = useState(null)

  const filteredEntries = useMemo(() => {
    const normalizedSearch = searchValue.trim().toLowerCase()

    return entries
      .filter((entry) => {
        const project = getMockProjectById(entry.projectId)

        if (projectFilter !== 'all' && entry.projectId !== projectFilter) {
          return false
        }

        if (!matchesDateRange(entry.date, fromDate, toDate)) {
          return false
        }

        if (!normalizedSearch) {
          return true
        }

        return [entry.description, entry.focus, project?.name || '']
          .join(' ')
          .toLowerCase()
          .includes(normalizedSearch)
      })
      .map((entry) => ({
        ...entry,
        project: getMockProjectById(entry.projectId),
      }))
      .sort((left, right) => right.date.localeCompare(left.date))
  }, [entries, projectFilter, searchValue, fromDate, toDate])

  const filteredTotals = useMemo(() => {
    const totalMinutes = filteredEntries.reduce((sum, entry) => sum + entry.durationMinutes, 0)
    const uniqueProjects = new Set(filteredEntries.map((entry) => entry.projectId)).size

    return {
      totalEntries: filteredEntries.length,
      totalMinutes,
      uniqueProjects,
    }
  }, [filteredEntries])

  function closeFormModal() {
    setFormState({ mode: null, entry: null })
  }

  function handleSaveEntry(values) {
    const nextTimestamp = '2026-04-17T12:00:00'

    if (formState.mode === 'edit' && formState.entry) {
      setEntries((current) =>
        current.map((entry) =>
          entry.id === formState.entry.id
            ? {
                ...entry,
                projectId: values.projectId,
                date: values.date,
                durationMinutes: values.durationMinutes,
                description: values.description,
                focus: buildFocusLabel(values.description),
                updatedAt: nextTimestamp,
              }
            : entry,
        ),
      )
      closeFormModal()
      return
    }

    const newEntry = {
      id: `entry-${Date.now()}`,
      projectId: values.projectId,
      date: values.date,
      durationMinutes: values.durationMinutes,
      description: values.description,
      loggedBy: 'Alex Johnson',
      createdAt: nextTimestamp,
      updatedAt: nextTimestamp,
      focus: buildFocusLabel(values.description),
      tags: [],
    }

    setEntries((current) => [newEntry, ...current])
    closeFormModal()
  }

  return (
    <section className="entries-page stack-lg">
      <div className="dashboard-card entries-filters-card">
        <div className="entries-filters-grid">
          <label className="field entries-search-field" htmlFor="entry-search">
            Search entries
            <input
              id="entry-search"
              type="search"
              value={searchValue}
              onChange={(event) => setSearchValue(event.target.value)}
              placeholder="Search by description, focus, or project"
            />
          </label>

          <label className="field" htmlFor="entry-project-filter">
            Project
            <select
              id="entry-project-filter"
              value={projectFilter}
              onChange={(event) => setProjectFilter(event.target.value)}
            >
              <option value="all">All projects</option>
              {MOCK_PROJECTS.map((project) => (
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

        {filteredEntries.length ? (
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
                        <span className={`entry-project-avatar ${entry.project?.accent || 'blue'}`} aria-hidden="true">
                          {getProjectInitials(entry.project?.name || 'Project')}
                        </span>
                        <div>
                          <strong>{entry.project?.name}</strong>
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
                          aria-label={`Edit ${entry.project?.name} entry on ${formatDate(entry.date)}`}
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
                          aria-label={`Delete ${entry.project?.name} entry on ${formatDate(entry.date)}`}
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
        entry={formState.entry}
        projects={MOCK_PROJECTS}
        onClose={closeFormModal}
        onSave={handleSaveEntry}
      />

      <ConfirmDeleteModal
        isOpen={Boolean(entryToDelete)}
        description={entryToDelete?.description}
        onCancel={() => setEntryToDelete(null)}
        onConfirm={() => {
          setEntries((current) => current.filter((entry) => entry.id !== entryToDelete.id))
          setEntryToDelete(null)
        }}
      />
    </section>
  )
}

export default TimeEntriesPage
