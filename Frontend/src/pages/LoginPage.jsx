import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import { getApiErrorMessage } from '../services/apiError'
import logoImage from '../../../Documentation/images/logo.png'

function LoginPage() {
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState(location.state?.email || '')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState('')
  const [successMessage] = useState(location.state?.message || '')

  const redirectPath = location.state?.from?.pathname || '/dashboard'

  const onSubmit = async (event) => {
    event.preventDefault()
    setError('')

    if (!email.trim() || !password) {
      setError('Email and password are required.')
      return
    }

    try {
      await login({
        email: email.trim(),
        password,
        rememberMe,
      })
      navigate(redirectPath, { replace: true })
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Login failed. Please check your credentials and try again.'))
    }
  }

  return (
    <main className="app-frame">
      <section className="login-shell">
        <section className="login-panel">
          <form className="login-card" onSubmit={onSubmit} noValidate>
            <Link to="/" className="brand-mark login-brand" aria-label="TimeSync home">
              <img src={logoImage} className="brand-logo login-logo" alt="TimeSync" />
            </Link>

            <label className="field" htmlFor="email">
              Email
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                disabled={isLoading}
                required
              />
            </label>

            <label className="field" htmlFor="password">
              Password
              <div className="password-input-wrap">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  disabled={isLoading}
                  required
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowPassword((current) => !current)}
                  disabled={isLoading}
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
            </label>

            <div className="login-row">
              <label className="remember-choice" htmlFor="rememberMe">
                <input
                  id="rememberMe"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(event) => setRememberMe(event.target.checked)}
                  disabled={isLoading}
                />
                <span>Remember me</span>
              </label>

              <Link to="/forgot-password" className="inline-link">
                Forgot password?
              </Link>
            </div>

            {error ? <p className="error">{error}</p> : null}
            {successMessage ? <p className="success">{successMessage}</p> : null}

            <button className="btn-primary login-submit" type="submit" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Log In'}
            </button>

            <p className="muted login-footer-text">
              Don&apos;t have an account? <Link to="/signup" className="inline-link">Sign up</Link>
            </p>
          </form>
        </section>
      </section>
    </main>
  )
}

export default LoginPage
