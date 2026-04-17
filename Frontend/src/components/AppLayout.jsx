import { useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import logoImage from '../../../Documentation/images/logo.png'

const MOCK_NOTIFICATIONS = [
  { id: 'n1', message: 'You were added to Project Alpha', created_at: '2026-04-16T11:20:00' },
  { id: 'n2', message: 'New project Marketing Campaign created', created_at: '2026-04-15T10:15:00' },
  { id: 'n3', message: 'Time entry approved by manager', created_at: '2026-04-14T09:00:00' },
]

function timeAgo(dateString) {
  const diff = Math.floor((Date.now() - new Date(dateString)) / (1000 * 60 * 60 * 24))
  if (diff <= 0) return 'Today'
  if (diff === 1) return '1 day ago'
  return `${diff} days ago`
}

function AppLayout() {
  const { logout } = useAuth()
  const [notifOpen, setNotifOpen] = useState(false)

  return (
    <div className="workspace-shell">
      <aside className="workspace-sidebar">
        <Link to="/dashboard" className="workspace-logo" aria-label="TimeSync dashboard home">
          <img src={logoImage} className="workspace-logo-img" alt="TimeSync" />
        </Link>

        <nav className="workspace-menu" aria-label="Main navigation">
          <NavLink to="/dashboard" className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}>
            <span className="menu-icon" aria-hidden="true">◫</span>
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/projects" className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}>
            <span className="menu-icon" aria-hidden="true">◻</span>
            <span>Projects</span>
          </NavLink>
          <NavLink to="/time-entries" className={({ isActive }) => `menu-item ${isActive ? 'active' : ''}`}>
            <span className="menu-icon" aria-hidden="true">◷</span>
            <span>My Entries</span>
          </NavLink>
        </nav>

        <button className="menu-item logout-item" onClick={logout} type="button">
          <span className="menu-icon" aria-hidden="true">⏻</span>
          <span>Logout</span>
        </button>
      </aside>

      <section className="workspace-main">
        <header className="workspace-header">
          <h1>Dashboard</h1>
          <div className="workspace-header-actions" aria-label="User and alerts">
            <div
              className="notify-wrap"
              onMouseEnter={() => setNotifOpen(true)}
              onMouseLeave={() => setNotifOpen(false)}
            >
              <Link to="/notifications" className="notify-btn" aria-label="Open notifications">
                <span className="notify-icon" aria-hidden="true">🔔</span>
                <span className="notify-badge">{MOCK_NOTIFICATIONS.length}</span>
              </Link>
              {notifOpen && (
                <div className="notif-popup" role="menu">
                  <p className="notif-popup-title">Notifications</p>
                  <ul>
                    {MOCK_NOTIFICATIONS.map((n) => (
                      <li key={n.id}>
                        <span className="notif-popup-msg">{n.message}</span>
                        <span className="notif-popup-time">{timeAgo(n.created_at)}</span>
                      </li>
                    ))}
                  </ul>
                  <Link to="/notifications" className="notif-popup-link">View all</Link>
                </div>
              )}
            </div>
            <Link to="/profile" className="profile-btn" aria-label="Open profile">
              <span className="profile-avatar" aria-hidden="true">A</span>
              <span>Alex</span>
              <span className="profile-caret" aria-hidden="true">▾</span>
            </Link>
          </div>
        </header>

        <main className="workspace-content">
          <Outlet />
        </main>
      </section>
    </div>
  )
}

export default AppLayout
