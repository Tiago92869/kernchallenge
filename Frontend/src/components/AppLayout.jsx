import { Link, NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'

function AppLayout() {
  const { logout } = useAuth()

  return (
    <div>
      <header className="topbar">
        <div className="topbar-inner page">
          <Link to="/dashboard" className="brand">Timesheet</Link>
          <nav className="nav">
            <NavLink to="/dashboard">Dashboard</NavLink>
            <NavLink to="/projects">Projects</NavLink>
            <NavLink to="/time-entries">Time Entries</NavLink>
            <NavLink to="/notifications">Notifications</NavLink>
          </nav>
          <button className="btn ghost" onClick={logout} type="button">Logout</button>
        </div>
      </header>
      <main className="page">
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout
