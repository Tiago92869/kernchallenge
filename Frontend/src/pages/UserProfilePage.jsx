import { useEffect, useMemo, useState } from 'react'

import { useAuth } from '../hooks/useAuth'
import { apiClient } from '../services/apiClient'

function getPasswordStrength(password) {
  if (!password) return { score: 0, label: '' }
  let score = 0
  if (password.length >= 8) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[^A-Za-z0-9]/.test(password)) score += 1
  if (score <= 1) return { score, label: 'Weak' }
  if (score <= 3) return { score, label: 'Medium' }
  return { score, label: 'Strong' }
}

const EyeIcon = ({ open }) =>
  open ? (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M2.9 4.3 1.5 5.7 5 9.2C3.6 10.4 2.4 11.9 1.5 13.8c2 4.1 6.1 6.7 10.5 6.7 2.2 0 4.2-.6 6-1.7l4.1 4.1 1.4-1.4ZM8.2 12.4l3.4 3.4a2.9 2.9 0 0 1-3.4-3.4Zm4.9 4.9-4-4a2.9 2.9 0 0 1 4 4Zm-1.1-13.8c4.4 0 8.5 2.6 10.5 6.7-.8 1.6-1.8 3-3.1 4.1L16.8 12A4.9 4.9 0 0 0 12 7.1a4.8 4.8 0 0 0-1.4.2L7.8 4.5A11 11 0 0 1 12 3.5Z" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 5c4.4 0 8.5 2.6 10.5 7-2 4.4-6.1 7-10.5 7S3.5 16.4 1.5 12C3.5 7.6 7.6 5 12 5Zm0 2C8.7 7 5.7 8.8 4 12c1.7 3.2 4.7 5 8 5s6.3-1.8 8-5c-1.7-3.2-4.7-5-8-5Zm0 2.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5Z" />
    </svg>
  )

function parseUserIdFromToken(token) {
  if (!token) return null
  const parts = token.split('.')
  if (parts.length < 2) return null
  try {
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const payload = JSON.parse(atob(base64))
    return payload?.sub || null
  } catch {
    return null
  }
}

function formatMemberSince(dateString) {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
}

function UserProfilePage() {
  const { token } = useAuth()
  const [user, setUser] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [draftFirst, setDraftFirst] = useState('')
  const [draftLast, setDraftLast] = useState('')
  const [saveError, setSaveError] = useState(null)

  // password modal state
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [pwCurrent, setPwCurrent] = useState('')
  const [pwNew, setPwNew] = useState('')
  const [pwConfirm, setPwConfirm] = useState('')
  const [showPwCurrent, setShowPwCurrent] = useState(false)
  const [showPwNew, setShowPwNew] = useState(false)
  const [showPwConfirm, setShowPwConfirm] = useState(false)
  const [pwSubmitted, setPwSubmitted] = useState(false)
  const [pwError, setPwError] = useState(null)
  const [pwSuccess, setPwSuccess] = useState(false)
  const [pwSaving, setPwSaving] = useState(false)

  const passwordStrength = useMemo(() => getPasswordStrength(pwNew), [pwNew])

  useEffect(() => {
    let isCancelled = false
    const userId = parseUserIdFromToken(token)
    if (!userId) return () => { isCancelled = true }

    apiClient.get(`/users/${userId}`).then((response) => {
      if (isCancelled) return
      const data = response?.data?.data
      if (data) setUser(data)
    }).catch(() => {})

    return () => { isCancelled = true }
  }, [token])

  function handleEdit() {
    setDraftFirst(user?.firstname || '')
    setDraftLast(user?.lastname || '')
    setSaveError(null)
    setIsEditing(true)
  }

  async function handleSave() {
    const userId = parseUserIdFromToken(token)
    if (!userId) return

    const trimmedFirst = draftFirst.trim()
    const trimmedLast = draftLast.trim()

    if (!trimmedFirst || !trimmedLast) {
      setSaveError('First and last name are required.')
      return
    }

    try {
      const response = await apiClient.put(`/users/${userId}`, {
        firstname: trimmedFirst,
        lastname: trimmedLast,
        email: user?.email,
      })
      const updated = response?.data?.data
      if (updated) setUser(updated)
      setIsEditing(false)
      setSaveError(null)
    } catch {
      setSaveError('Failed to save changes. Please try again.')
    }
  }

  function handleCancel() {
    setIsEditing(false)
    setSaveError(null)
  }

  function openPasswordModal() {
    setPwCurrent('')
    setPwNew('')
    setPwConfirm('')
    setShowPwCurrent(false)
    setShowPwNew(false)
    setShowPwConfirm(false)
    setPwSubmitted(false)
    setPwError(null)
    setPwSuccess(false)
    setIsChangingPassword(true)
  }

  function closePasswordModal() {
    setIsChangingPassword(false)
    setPwError(null)
    setPwSuccess(false)
  }

  async function handlePasswordSave() {
    setPwSubmitted(true)
    if (!pwCurrent || !pwNew || !pwConfirm) {
      setPwError('All fields are required.')
      return
    }
    if (pwNew !== pwConfirm) {
      setPwError('New passwords do not match.')
      return
    }
    if (passwordStrength.score < 2) {
      setPwError('New password is too weak.')
      return
    }

    const userId = parseUserIdFromToken(token)
    if (!userId) return

    setPwSaving(true)
    setPwError(null)
    try {
      await apiClient.put(`/users/password/${userId}`, {
        old_password: pwCurrent,
        new_password: pwNew,
      })
      setPwSuccess(true)
      setPwSaving(false)
    } catch (err) {
      const msg = err?.response?.data?.message || 'Failed to update password. Please try again.'
      setPwError(msg)
      setPwSaving(false)
    }
  }

  const firstName = user?.firstname || ''
  const lastName = user?.lastname || ''
  const email = user?.email || ''
  const initials = `${firstName[0] || ''}${lastName[0] || ''}`.toUpperCase() || 'U'

  return (
    <section className="profile-page">
      <div className="dashboard-card profile-card">
        <div className="profile-avatar-large" aria-hidden="true">{initials}</div>
        <div className="profile-info">
          <h2>{[firstName, lastName].filter(Boolean).join(' ') || '—'}</h2>
          <span className="status-badge public">Active</span>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>Account Details</h2>
          <div className="profile-card-actions">
            <button type="button" className="btn-secondary profile-pw-btn" onClick={openPasswordModal}>
              Reset Password
            </button>
            <button type="button" className="profile-edit-btn" onClick={handleEdit} title="Edit name">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            Edit
          </button>
          </div>
        </div>

        <div className="profile-details-grid">
          <div className="profile-field">
            <label>First Name</label>
            <p>{firstName || '—'}</p>
          </div>
          <div className="profile-field">
            <label>Last Name</label>
            <p>{lastName || '—'}</p>
          </div>
          <div className="profile-field">
            <label>Email</label>
            <p>{email || '—'}</p>
          </div>
          <div className="profile-field">
            <label>Member Since</label>
            <p>{formatMemberSince(user?.created_at)}</p>
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
                {saveError && <p className="error">{saveError}</p>}
                <button type="button" className="btn-secondary" onClick={handleCancel}>Cancel</button>
                <button type="button" className="btn-primary" onClick={handleSave}>Save Changes</button>
              </div>
            </div>
          </article>
        </div>
      )}

      {isChangingPassword && (
        <div className="modal-overlay" role="presentation" onClick={closePasswordModal}>
          <article
            className="modal-card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="reset-pw-title"
            onClick={(e) => e.stopPropagation()}
          >
            <header className="modal-head project-form-head">
              <h2 id="reset-pw-title">Reset Password</h2>
              <button type="button" className="project-form-close" onClick={closePasswordModal} aria-label="Close">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M18.3 5.7 12 12l6.3 6.3-1.4 1.4L10.6 13.4 4.3 19.7 2.9 18.3 9.2 12 2.9 5.7l1.4-1.4 6.3 6.3 6.3-6.3z" />
                </svg>
              </button>
            </header>

            <div className="modal-body stack-sm">
              {pwSuccess ? (
                <>
                  <p className="success">Password updated successfully.</p>
                  <div className="modal-actions">
                    <button type="button" className="btn-primary" onClick={closePasswordModal}>Close</button>
                  </div>
                </>
              ) : (
                <>
                  {/* Current password — eye icon only */}
                  <label className="field" htmlFor="pw-current">
                    Current Password
                    <div className="password-input-wrap">
                      <input
                        id="pw-current"
                        type={showPwCurrent ? 'text' : 'password'}
                        className="form-input"
                        value={pwCurrent}
                        onChange={(e) => setPwCurrent(e.target.value)}
                        autoComplete="current-password"
                        autoFocus
                      />
                      <button
                        type="button"
                        className="password-toggle-btn"
                        onClick={() => setShowPwCurrent((v) => !v)}
                        aria-label={showPwCurrent ? 'Hide password' : 'Show password'}
                      >
                        <EyeIcon open={showPwCurrent} />
                      </button>
                    </div>
                    {pwSubmitted && !pwCurrent && <span className="error">Current password is required.</span>}
                  </label>

                  {/* New password — eye icon + strength meter */}
                  <label className="field" htmlFor="pw-new">
                    New Password
                    <div className="password-input-wrap">
                      <input
                        id="pw-new"
                        type={showPwNew ? 'text' : 'password'}
                        className="form-input"
                        value={pwNew}
                        onChange={(e) => setPwNew(e.target.value)}
                        autoComplete="new-password"
                      />
                      <button
                        type="button"
                        className="password-toggle-btn"
                        onClick={() => setShowPwNew((v) => !v)}
                        aria-label={showPwNew ? 'Hide password' : 'Show password'}
                      >
                        <EyeIcon open={showPwNew} />
                      </button>
                    </div>
                    {pwNew && (
                      <div className="password-strength-wrap" aria-live="polite">
                        <div className="password-strength-bars" role="presentation">
                          {[1, 2, 3, 4].map((step) => (
                            <span
                              key={step}
                              className={`password-strength-bar ${step <= passwordStrength.score ? 'active' : ''} ${passwordStrength.label.toLowerCase()}`}
                            />
                          ))}
                        </div>
                        <span className={`password-strength-text ${passwordStrength.label.toLowerCase()}`}>
                          Strength: {passwordStrength.label}
                        </span>
                      </div>
                    )}
                    {pwSubmitted && !pwNew && <span className="error">New password is required.</span>}
                  </label>

                  {/* Confirm password — real-time match indicator + eye icon */}
                  <label className="field" htmlFor="pw-confirm">
                    Confirm New Password
                    <div className="password-input-wrap">
                      <input
                        id="pw-confirm"
                        type={showPwConfirm ? 'text' : 'password'}
                        className="form-input"
                        value={pwConfirm}
                        onChange={(e) => setPwConfirm(e.target.value)}
                        autoComplete="new-password"
                      />
                      <button
                        type="button"
                        className="password-toggle-btn"
                        onClick={() => setShowPwConfirm((v) => !v)}
                        aria-label={showPwConfirm ? 'Hide password' : 'Show password'}
                      >
                        <EyeIcon open={showPwConfirm} />
                      </button>
                    </div>
                    {pwConfirm && (
                      <span className={pwNew === pwConfirm ? 'success' : 'error'} aria-live="polite">
                        {pwNew === pwConfirm ? 'Passwords match.' : 'Passwords do not match.'}
                      </span>
                    )}
                    {pwSubmitted && !pwConfirm && <span className="error">Please confirm your new password.</span>}
                  </label>

                  <div className="modal-actions">
                    {pwError && <p className="error">{pwError}</p>}
                    <button type="button" className="btn-secondary" onClick={closePasswordModal} disabled={pwSaving}>Cancel</button>
                    <button type="button" className="btn-primary" onClick={handlePasswordSave} disabled={pwSaving}>
                      {pwSaving ? 'Saving…' : 'Update Password'}
                    </button>
                  </div>
                </>
              )}
            </div>
          </article>
        </div>
      )}
    </section>
  )
}

export default UserProfilePage
