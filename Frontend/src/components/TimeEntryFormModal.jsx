import { useState } from 'react'

function toTimeValue(durationMinutes) {
  const hours = Math.floor((durationMinutes || 0) / 60)
  const minutes = (durationMinutes || 0) % 60
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}

function toDurationMinutes(timeValue) {
  const [hours = '0', minutes = '0'] = (timeValue || '00:00').split(':')
  return Number(hours) * 60 + Number(minutes)
}

function buildInitialValues(entry, projects) {
  return {
    projectId: entry?.projectId || projects[0]?.id || '',
    date: entry?.date || '2026-04-17',
    timeValue: toTimeValue(entry?.durationMinutes || 60),
    description: entry?.description || '',
  }
}

function TimeEntryFormModal({ isOpen, mode, entry, projects, onClose, onSave }) {
  const [values, setValues] = useState(() => buildInitialValues(entry, projects))

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
            onSave({
              ...values,
              durationMinutes: toDurationMinutes(values.timeValue),
            })
          }}
        >
          <label className="field" htmlFor="time-entry-project">
            Project
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

          <label className="field" htmlFor="time-entry-time">
            Time
            <input
              id="time-entry-time"
              type="time"
              step="60"
              value={values.timeValue}
              onChange={(event) => setValues((current) => ({ ...current, timeValue: event.target.value }))}
              required
            />
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