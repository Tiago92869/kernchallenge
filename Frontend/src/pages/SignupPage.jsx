import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

function SignupPage() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSignup = () => {
    login()
    navigate('/dashboard')
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <h1>Sign Up</h1>
        <p className="muted-text">
          Placeholder sign-up screen for now. This action sets a mock session.
        </p>
        <button type="button" className="btn-primary" onClick={handleSignup}>
          Create account and continue
        </button>
        <p className="muted-text">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </section>
    </main>
  )
}

export default SignupPage
