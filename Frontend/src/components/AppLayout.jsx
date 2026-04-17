import { useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'

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

const ROUTE_TITLES = [
  { pattern: /^\/time-entries\/[^/]+/, title: 'Time Entry Details', back: true },
  { pattern: /^\/time-entries/, title: 'My Entries' },
  { pattern: /^\/projects\/[^/]+/, title: 'Project Details', back: true },
  { pattern: /^\/projects/, title: 'Projects' },
  { pattern: /^\/profile/, title: 'Profile' },
  { pattern: /^\/notifications/, title: 'Notifications' },
  { pattern: /^\/dashboard/, title: 'Dashboard' },
]

function usePageMeta() {
  const { pathname } = useLocation()
  for (const route of ROUTE_TITLES) {
    if (route.pattern.test(pathname)) {
      return { title: route.title, back: !!route.back }
    }
  }
  return { title: 'Dashboard', back: false }
}

function AppLayout() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [notifOpen, setNotifOpen] = useState(false)
  const { title, back } = usePageMeta()

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
          <div className="workspace-page-title">
            {back && (
              <button type="button" className="entry-back-link" onClick={() => navigate(-1)} aria-label="Go back">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M14.7 5.3 8 12l6.7 6.7 1.4-1.4L10.8 12l5.3-5.3z" />
                </svg>
              </button>
            )}
            <h1>{title}</h1>
          </div>
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
