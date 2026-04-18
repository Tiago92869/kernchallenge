import { useState } from 'react'

function buildInitialValues(project) {
  return {
    name: project?.name || '',
    description: project?.description || '',
    visibility: project?.visibility || 'PUBLIC',
  }
}

function ProjectCreateModal({ isOpen, onClose, onSave, mode = 'create', project = null }) {
  const isEdit = mode === 'edit'
  const [values, setValues] = useState(() => buildInitialValues(project))

  if (!isOpen) {
    return null
  }

  function handleChange(field, value) {
    setValues((current) => ({ ...current, [field]: value }))
  }

  function handleSubmit(event) {
    event.preventDefault()
    const trimmedName = values.name.trim()
    if (!trimmedName) {
      return
    }

    onSave({
      name: trimmedName,
      description: values.description.trim(),
      visibility: values.visibility,
    })

    setValues(buildInitialValues(project))
  }

  function handleClose() {
    setValues(buildInitialValues(project))
    onClose()
  }

  return (
    <div className="modal-overlay" role="presentation" onClick={handleClose}>
      <article
        className="modal-card project-form-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="project-create-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-head project-form-head">
          <h2 id="project-create-title">{isEdit ? 'Edit Project' : 'Create Project'}</h2>
          <button type="button" className="project-form-close" onClick={handleClose} aria-label="Close project modal">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M18.3 5.7 12 12l6.3 6.3-1.4 1.4L10.6 13.4 4.3 19.7 2.9 18.3 9.2 12 2.9 5.7l1.4-1.4 6.3 6.3 6.3-6.3z" />
            </svg>
          </button>
        </header>

        <form className="project-form-content" onSubmit={handleSubmit}>
          <div className="modal-body stack-sm project-form-body">
          <label className="field" htmlFor="project-create-name">
            Project name
            <input
              id="project-create-name"
              type="text"
              value={values.name}
              onChange={(event) => handleChange('name', event.target.value)}
              placeholder="Type project name"
              required
            />
          </label>

          <label className="field" htmlFor="project-create-description">
            Description
            <textarea
              id="project-create-description"
              className="entry-modal-textarea"
              value={values.description}
              onChange={(event) => handleChange('description', event.target.value)}
              placeholder="Write a short project description"
              rows={4}
            />
          </label>

          <fieldset className="project-visibility-group">
            <legend>Visibility</legend>
            <div className="project-visibility-options">
              <button
                type="button"
                className={`project-visibility-option ${values.visibility === 'PUBLIC' ? 'active' : ''}`}
                onClick={() => handleChange('visibility', 'PUBLIC')}
                aria-pressed={values.visibility === 'PUBLIC'}
              >
                <span className="project-visibility-check" aria-hidden="true" />
                <span className="project-visibility-copy">
                  <strong>Public</strong>
                  <small>Visible to all team members</small>
                </span>
              </button>

              <button
                type="button"
                className={`project-visibility-option ${values.visibility === 'PRIVATE' ? 'active' : ''}`}
                onClick={() => handleChange('visibility', 'PRIVATE')}
                aria-pressed={values.visibility === 'PRIVATE'}
              >
                <span className="project-visibility-check" aria-hidden="true" />
                <span className="project-visibility-copy">
                  <strong>Private</strong>
                  <small>Only invited members can view</small>
                </span>
              </button>
            </div>
          </fieldset>
          </div>

          <div className="project-form-footer">
            <div className="modal-actions project-form-actions">
            <button type="button" className="btn-secondary" onClick={handleClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              {isEdit ? 'Save Changes' : 'Create Project'}
            </button>
            </div>
          </div>
        </form>
      </article>
    </div>
  )
}

export default ProjectCreateModal
