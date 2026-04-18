import { useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import { MOCK_NOTIFICATIONS } from '../mocks/notifications'
import logoImage from '../../../Documentation/images/logo.png'

function timeAgo(dateString) {
  const created = new Date(dateString).getTime()
  const diffMs = Math.max(0, Date.now() - created)
  const oneHour = 60 * 60 * 1000
  const oneDay = 24 * oneHour
  if (diffMs < oneHour) return `${Math.max(1, Math.floor(diffMs / (60 * 1000)))}m ago`
  if (diffMs < oneDay) return `${Math.floor(diffMs / oneHour)}h ago`
  if (diffMs < oneDay * 2) return 'Yesterday'
  return new Date(dateString).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

const ROUTE_TITLES = [
  { pattern: /^\/time-entries\/[^/]+/, title: 'Time Entry Details', back: true },
  { pattern: /^\/time-entries/, title: 'My Entries' },
  { pattern: /^\/projects\/[^/]+\/members$/, title: 'Project Members', back: true },
  { pattern: /^\/projects\/[^/]+$/, title: 'Project Details', back: true },
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

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }
  const { title, back } = usePageMeta()
  const unreadCount = MOCK_NOTIFICATIONS.filter((item) => !item.isRead).length

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

        <button className="menu-item logout-item" onClick={handleLogout} type="button">
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
                <span className="notify-badge">{unreadCount}</span>
              </Link>
              {notifOpen && (
                <div className="notif-popup" role="menu">
                  <p className="notif-popup-title">Notifications</p>
                  <ul>
                    {MOCK_NOTIFICATIONS.slice(0, 4).map((n) => (
                      <li key={n.id}>
                        <Link
                          to={`/notifications?open=${encodeURIComponent(n.id)}`}
                          className="notif-popup-item"
                          onClick={() => setNotifOpen(false)}
                        >
                          <span className="notif-popup-msg">{n.message}</span>
                          <span className="notif-popup-time">{timeAgo(n.createdAt)}</span>
                        </Link>
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
