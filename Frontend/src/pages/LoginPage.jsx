import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import logoImage from '../../../Documentation/images/logo.png'

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isLoading } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState('')

  const fromPath = location.state?.from?.pathname || '/dashboard'

  const onSubmit = async (event) => {
    event.preventDefault()
    setError('')

    try {
      await login({ email, password })
      navigate(fromPath, { replace: true })
    } catch {
      setError('Invalid email or password')
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
                required
              />
            </label>

            <label className="field" htmlFor="password">
              Password
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </label>

            <div className="login-row">
              <label className="remember-choice" htmlFor="rememberMe">
                <input
                  id="rememberMe"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(event) => setRememberMe(event.target.checked)}
                />
                <span>Remember me</span>
              </label>

              <Link to="/forgot-password" className="inline-link">
                Forgot password?
              </Link>
            </div>

            {error ? <p className="error">{error}</p> : null}

            <button className="btn-primary login-submit" type="submit" disabled={isLoading}>
              {isLoading ? 'Logging In...' : 'Log In'}
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
