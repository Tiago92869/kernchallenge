import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleLogin = () => {
    login()
    navigate('/dashboard')
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <h1>Log In</h1>
        <p className="muted-text">
          Placeholder login screen for now. This action sets a mock session.
        </p>
        <button type="button" className="btn-primary" onClick={handleLogin}>
          Continue to Dashboard
        </button>
        <p className="muted-text">
          Need an account? <Link to="/signup">Create one</Link>
        </p>
      </section>
    </main>
  )
}

export default LoginPage
