import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { getApiErrorMessage } from '../services/apiError'
import { createAccountRequest } from '../services/authService'
import heroImage from '../../../Documentation/images/land_page_image.png'
import logoImage from '../../../Documentation/images/logo.png'

function getPasswordStrength(password) {
  if (!password) {
    return { score: 0, label: '' }
  }

  let score = 0
  if (password.length >= 8) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/[0-9]/.test(password)) score += 1
  if (/[^A-Za-z0-9]/.test(password)) score += 1

  if (score <= 1) return { score, label: 'Weak' }
  if (score <= 3) return { score, label: 'Medium' }
  return { score, label: 'Strong' }
}

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
  const navigate = useNavigate()

  const [values, setValues] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [hasSubmitted, setHasSubmitted] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const errors = useMemo(() => validate(values), [values])
  const passwordStrength = useMemo(() => getPasswordStrength(values.password), [values.password])

  const confirmPasswordHasValue = values.confirmPassword.length > 0
  const passwordsMatch = values.password === values.confirmPassword

  const onChange = (event) => {
    const { name, value } = event.target
    setValues((prev) => ({ ...prev, [name]: value }))
    if (successMessage) {
      setSuccessMessage('')
    }
    if (submitError) {
      setSubmitError('')
    }
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    setHasSubmitted(true)
    setSubmitError('')
    setSuccessMessage('')

    if (Object.keys(errors).length > 0) {
      return
    }

    setIsSubmitting(true)
    try {
      await createAccountRequest({
        email: values.email.trim(),
        firstname: values.firstName.trim(),
        lastname: values.lastName.trim(),
        password: values.password,
      })

      navigate('/login', {
        replace: true,
        state: {
          email: values.email.trim(),
          message: 'Account created successfully. You can now log in.',
        },
      })
    } catch (requestError) {
      setSubmitError(getApiErrorMessage(requestError, 'Failed to create account. Please try again.'))
    } finally {
      setIsSubmitting(false)
    }
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
                    disabled={isSubmitting}
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
                    disabled={isSubmitting}
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
                  disabled={isSubmitting}
                  required
                />
                {hasSubmitted && errors.email ? <span className="error">{errors.email}</span> : null}
              </label>

              <label className="field" htmlFor="password">
                Password
                <div className="password-input-wrap">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={values.password}
                    onChange={onChange}
                    autoComplete="new-password"
                    disabled={isSubmitting}
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle-btn"
                    onClick={() => setShowPassword((current) => !current)}
                    disabled={isSubmitting}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M2.9 4.3 1.5 5.7 5 9.2C3.6 10.4 2.4 11.9 1.5 13.8c2 4.1 6.1 6.7 10.5 6.7 2.2 0 4.2-.6 6-1.7l4.1 4.1 1.4-1.4ZM8.2 12.4l3.4 3.4a2.9 2.9 0 0 1-3.4-3.4Zm4.9 4.9-4-4a2.9 2.9 0 0 1 4 4Zm-1.1-13.8c4.4 0 8.5 2.6 10.5 6.7-.8 1.6-1.8 3-3.1 4.1L16.8 12A4.9 4.9 0 0 0 12 7.1a4.8 4.8 0 0 0-1.4.2L7.8 4.5A11 11 0 0 1 12 3.5Z" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M12 5c4.4 0 8.5 2.6 10.5 7-2 4.4-6.1 7-10.5 7S3.5 16.4 1.5 12C3.5 7.6 7.6 5 12 5Zm0 2C8.7 7 5.7 8.8 4 12c1.7 3.2 4.7 5 8 5s6.3-1.8 8-5c-1.7-3.2-4.7-5-8-5Zm0 2.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5Z" />
                      </svg>
                    )}
                  </button>
                </div>
                {values.password ? (
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
                ) : null}
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
                  disabled={isSubmitting}
                  required
                />
                {hasSubmitted && errors.confirmPassword ? (
                  <span className="error">{errors.confirmPassword}</span>
                ) : null}
                {confirmPasswordHasValue && !hasSubmitted ? (
                  <span className={passwordsMatch ? 'success' : 'error'}>
                    {passwordsMatch ? 'Passwords match.' : 'Passwords do not match.'}
                  </span>
                ) : null}
              </label>

              {submitError ? <p className="error">{submitError}</p> : null}

              <button type="submit" className="btn-primary create-account-submit" disabled={isSubmitting}>
                {isSubmitting ? 'Creating account...' : 'Create Account'}
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
