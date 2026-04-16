import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import heroImage from '../../../Documentation/images/land_page_image.png'
import logoImage from '../../../Documentation/images/logo.png'

function validate(values) {
  const nextErrors = {}

  if (!values.firstName.trim()) {
    nextErrors.firstName = 'First name is required.'
  }
  if (!values.lastName.trim()) {
    nextErrors.lastName = 'Last name is required.'
  }
  if (!values.email.trim()) {
    nextErrors.email = 'Email is required.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    nextErrors.email = 'Please enter a valid email address.'
  }
  if (!values.password) {
    nextErrors.password = 'Password is required.'
  }
  if (!values.confirmPassword) {
    nextErrors.confirmPassword = 'Password confirmation is required.'
  } else if (values.password !== values.confirmPassword) {
    nextErrors.confirmPassword = 'Passwords do not match.'
  }

  return nextErrors
}

function CreateAccountPage() {
  const [values, setValues] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [hasSubmitted, setHasSubmitted] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  const errors = useMemo(() => validate(values), [values])

  const onChange = (event) => {
    const { name, value } = event.target
    setValues((prev) => ({ ...prev, [name]: value }))
    if (successMessage) {
      setSuccessMessage('')
    }
  }

  const onSubmit = (event) => {
    event.preventDefault()
    setHasSubmitted(true)

    if (Object.keys(errors).length > 0) {
      return
    }

    setSuccessMessage('Account data is valid. Backend registration can be connected next.')
  }

  return (
    <main className="app-frame">
      <section className="create-account-shell">
        <section className="create-account-panel">
          <div className="create-account-form-side">
            <Link to="/" className="brand-mark" aria-label="TimeSync home">
              <img src={logoImage} className="brand-logo" alt="TimeSync" />
            </Link>

            <h1>Create account</h1>

            <form className="create-account-form" onSubmit={onSubmit} noValidate>
              <div className="name-grid">
                <label className="field" htmlFor="firstName">
                  First Name
                  <input
                    id="firstName"
                    name="firstName"
                    value={values.firstName}
                    onChange={onChange}
                    autoComplete="given-name"
                    required
                  />
                  {hasSubmitted && errors.firstName ? <span className="error">{errors.firstName}</span> : null}
                </label>

                <label className="field" htmlFor="lastName">
                  Last Name
                  <input
                    id="lastName"
                    name="lastName"
                    value={values.lastName}
                    onChange={onChange}
                    autoComplete="family-name"
                    required
                  />
                  {hasSubmitted && errors.lastName ? <span className="error">{errors.lastName}</span> : null}
                </label>
              </div>

              <label className="field" htmlFor="email">
                Email
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={values.email}
                  onChange={onChange}
                  autoComplete="email"
                  required
                />
                {hasSubmitted && errors.email ? <span className="error">{errors.email}</span> : null}
              </label>

              <label className="field" htmlFor="password">
                Password
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={values.password}
                  onChange={onChange}
                  autoComplete="new-password"
                  required
                />
                {hasSubmitted && errors.password ? <span className="error">{errors.password}</span> : null}
              </label>

              <label className="field" htmlFor="confirmPassword">
                Confirm Password
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={values.confirmPassword}
                  onChange={onChange}
                  autoComplete="new-password"
                  required
                />
                {hasSubmitted && errors.confirmPassword ? (
                  <span className="error">{errors.confirmPassword}</span>
                ) : null}
              </label>

              <button type="submit" className="btn-primary create-account-submit">
                Create Account
              </button>

              {successMessage ? <p className="success">{successMessage}</p> : null}

              <p className="muted">
                Already have an account? <Link to="/login" className="inline-link">Log in</Link>
              </p>
            </form>
          </div>

          <aside className="create-account-visual-side" aria-hidden="true">
            <img src={heroImage} className="create-account-hero" alt="" loading="eager" decoding="async" />
          </aside>
        </section>
      </section>
    </main>
  )
}

export default CreateAccountPage
