import { useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

function DashboardPage() {
  const navigate = useNavigate()
  const { logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <h1>Dashboard</h1>
        <p className="muted-text">
          Protected placeholder page. You are seeing this because mock auth is active.
        </p>
        <button type="button" className="btn-primary" onClick={handleLogout}>
          Log out
        </button>
      </section>
    </main>
  )
}

export default DashboardPage
