import { useState } from 'react'

function toDurationValue(durationMinutes) {
  const hours = Math.floor((durationMinutes || 0) / 60)
  const minutes = (durationMinutes || 0) % 60

  if (minutes === 0) {
    return `${hours}h`
  }

  return `${hours}:${String(minutes).padStart(2, '0')}h`
}

function toDurationMinutes(durationValue) {
  const normalized = (durationValue || '').toLowerCase().replace(/\s+/g, '')

  const hmMatch = normalized.match(/^(\d+):(\d{1,2})h?$/)
  if (hmMatch) {
    const hours = Number(hmMatch[1])
    const minutes = Number(hmMatch[2])
    if (minutes >= 60) return 0
    return hours * 60 + minutes
  }

  const hoursMatch = normalized.match(/^(\d+(?:[.,]\d+)?)h$/)
  if (hoursMatch) {
    const hours = Number(hoursMatch[1].replace(',', '.'))
    return Math.round(hours * 60)
  }

  const minutesMatch = normalized.match(/^(\d+)m$/)
  if (minutesMatch) {
    return Number(minutesMatch[1])
  }

  return 0
}

function buildInitialValues(entry, projects, lockedProjectId) {
  return {
    projectId: lockedProjectId || entry?.projectId || projects[0]?.id || '',
    date: entry?.date || '2026-04-17',
    durationValue: toDurationValue(entry?.durationMinutes || 60),
    description: entry?.description || '',
  }
}

function TimeEntryFormModal({ isOpen, mode, entry, projects, onClose, onSave, lockedProjectId = null }) {
  const [values, setValues] = useState(() => buildInitialValues(entry, projects, lockedProjectId))

  if (!isOpen) {
    return null
  }

  const title = mode === 'edit' ? 'Edit Time Entry' : 'Create New Entry'
  const actionLabel = mode === 'edit' ? 'Save Changes' : 'Create Entry'

  return (
    <div className="modal-overlay" role="presentation" onClick={onClose}>
      <div
        className="modal-card entry-form-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="time-entry-form-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-head">
          <h2 id="time-entry-form-title">{title}</h2>
        </div>

        <form
          className="modal-body stack-sm"
          onSubmit={(event) => {
            event.preventDefault()
            const durationMinutes = toDurationMinutes(values.durationValue)
            if (durationMinutes <= 0) {
              return
            }

            onSave({
              ...values,
              durationMinutes,
            })
          }}
        >
          <label className="field" htmlFor="time-entry-project">
            Project
            {lockedProjectId ? (
              <input
                id="time-entry-project"
                type="text"
                value={projects.find((project) => project.id === lockedProjectId)?.name || ''}
                disabled
                readOnly
              />
            ) : (
              <select
                id="time-entry-project"
                value={values.projectId}
                onChange={(event) => setValues((current) => ({ ...current, projectId: event.target.value }))}
              >
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
            )}
          </label>

          <label className="field" htmlFor="time-entry-date">
            Date
            <input
              id="time-entry-date"
              type="date"
              value={values.date}
              onChange={(event) => setValues((current) => ({ ...current, date: event.target.value }))}
              required
            />
          </label>

          <label className="field" htmlFor="time-entry-duration">
            Duration
            <input
              id="time-entry-duration"
              type="text"
              value={values.durationValue}
              onChange={(event) => setValues((current) => ({ ...current, durationValue: event.target.value }))}
              placeholder="e.g. 2h or 2:30h"
              required
            />
            <small className="muted">Use duration format, for example: 2h, 2:30h, or 150m.</small>
          </label>

          <label className="field" htmlFor="time-entry-description">
            Description
            <textarea
              id="time-entry-description"
              className="entry-modal-textarea"
              value={values.description}
              onChange={(event) => setValues((current) => ({ ...current, description: event.target.value }))}
              rows={5}
              required
            />
          </label>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              {actionLabel}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default TimeEntryFormModal