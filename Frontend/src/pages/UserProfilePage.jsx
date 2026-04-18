import { useState } from 'react'

function UserProfilePage() {
  const [isEditing, setIsEditing] = useState(false)
  const [firstName, setFirstName] = useState('Alex')
  const [lastName, setLastName] = useState('Johnson')
  const [draftFirst, setDraftFirst] = useState(firstName)
  const [draftLast, setDraftLast] = useState(lastName)

  function handleEdit() {
    setDraftFirst(firstName)
    setDraftLast(lastName)
    setIsEditing(true)
  }

  function handleSave() {
    setFirstName(draftFirst.trim() || firstName)
    setLastName(draftLast.trim() || lastName)
    setIsEditing(false)
  }

  function handleCancel() {
    setIsEditing(false)
  }

  const initials = `${firstName[0] || ''}${lastName[0] || ''}`.toUpperCase()

  return (
    <section className="profile-page">
      <div className="dashboard-card profile-card">
        <div className="profile-avatar-large" aria-hidden="true">{initials}</div>
        <div className="profile-info">
          <h2>{firstName} {lastName}</h2>
          <p className="muted">alex.johnson@example.com</p>
          <span className="status-badge public">Active</span>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>Account Details</h2>
          <button type="button" className="profile-edit-btn" onClick={handleEdit} title="Edit name">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            Edit
          </button>
        </div>

        <div className="profile-details-grid">
          <div className="profile-field">
            <label>First Name</label>
            <p>{firstName}</p>
          </div>
          <div className="profile-field">
            <label>Last Name</label>
            <p>{lastName}</p>
          </div>
          <div className="profile-field">
            <label>Email</label>
            <p>alex.johnson@example.com</p>
          </div>
          <div className="profile-field">
            <label>Member Since</label>
            <p>January 2026</p>
          </div>
        </div>
      </div>

      {isEditing && (
        <div className="modal-overlay" role="presentation" onClick={handleCancel}>
          <article
            className="modal-card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="edit-name-title"
            onClick={(e) => e.stopPropagation()}
          >
            <header className="modal-head project-form-head">
              <h2 id="edit-name-title">Edit Name</h2>
              <button type="button" className="project-form-close" onClick={handleCancel} aria-label="Close">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M18.3 5.7 12 12l6.3 6.3-1.4 1.4L10.6 13.4 4.3 19.7 2.9 18.3 9.2 12 2.9 5.7l1.4-1.4 6.3 6.3 6.3-6.3z" />
                </svg>
              </button>
            </header>

            <div className="modal-body stack-sm">
              <div className="profile-edit-row">
                <label className="field" htmlFor="profile-first-name">
                  First Name
                  <input
                    id="profile-first-name"
                    type="text"
                    className="form-input"
                    value={draftFirst}
                    onChange={(e) => setDraftFirst(e.target.value)}
                    autoFocus
                  />
                </label>
                <label className="field" htmlFor="profile-last-name">
                  Last Name
                  <input
                    id="profile-last-name"
                    type="text"
                    className="form-input"
                    value={draftLast}
                    onChange={(e) => setDraftLast(e.target.value)}
                  />
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={handleCancel}>Cancel</button>
                <button type="button" className="btn-primary" onClick={handleSave}>Save Changes</button>
              </div>
            </div>
          </article>
        </div>
      )}
    </section>
  )
}

export default UserProfilePage
