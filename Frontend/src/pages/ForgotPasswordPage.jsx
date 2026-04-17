import { useState } from 'react'
import { Link } from 'react-router-dom'

import logoImage from '../../../Documentation/images/logo.png'

function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const onSubmit = (event) => {
    event.preventDefault()
    setError('')
    setSuccessMessage('')

    if (!email.trim()) {
      setError('Email is required.')
      return
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address.')
      return
    }

    setSuccessMessage(
      'If this email exists in the system, a password will be sent to that account. Update it after you log in.',
    )
  }

  return (
    <main className="app-frame">
      <section className="login-shell">
        <section className="login-panel">
          <form className="login-card stack-sm" onSubmit={onSubmit} noValidate>
            <Link to="/" className="brand-mark login-brand" aria-label="TimeSync home">
              <img src={logoImage} className="brand-logo login-logo" alt="TimeSync" />
            </Link>

            <h1 className="login-title">Recover password</h1>

            <p className="muted-text">
              Provide the email linked to your account. A password will be sent to your email address, and you should update it after signing in.
            </p>

            <label className="field" htmlFor="recoveryEmail">
              Email
              <input
                id="recoveryEmail"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
              />
            </label>

            {error ? <p className="error">{error}</p> : null}
            {successMessage ? <p className="success">{successMessage}</p> : null}

            <button type="submit" className="btn-primary login-submit">
              Send recovery email
            </button>

            <p className="muted login-footer-text">
              Remembered your password? <Link to="/login" className="inline-link">Back to login</Link>
            </p>
          </form>
        </section>
      </section>
    </main>
  )
}

export default ForgotPasswordPage
