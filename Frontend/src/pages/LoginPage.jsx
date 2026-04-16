import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isLoading } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
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
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={onSubmit}>
        <h1>Sign In</h1>
        <p className="muted">Use your backend user credentials.</p>

        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        {error ? <p className="error">{error}</p> : null}

        <button className="btn" type="submit" disabled={isLoading}>
          {isLoading ? 'Signing in...' : 'Sign In'}
        </button>

        <p className="muted">
          Need an account? <Link to="/signup">Create one</Link>
        </p>
      </form>
    </div>
  )
}

export default LoginPage
