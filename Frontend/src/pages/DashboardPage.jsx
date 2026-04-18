import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

import {
  getDashboardActivity,
  getDashboardPreviewEntries,
  getDashboardProjectActivity,
  getNotificationsPreview,
  getTimeSummary,
} from '../services/dashboardService'

function startOfWeek(dateValue) {
  const copy = new Date(dateValue)
  const day = copy.getDay()
  const diff = day === 0 ? -6 : 1 - day
  copy.setDate(copy.getDate() + diff)
  copy.setHours(0, 0, 0, 0)
  return copy
}

function startOfMonth(dateValue) {
  const copy = new Date(dateValue)
  copy.setDate(1)
  copy.setHours(0, 0, 0, 0)
  return copy
}

function toISODate(dateValue) {
  return dateValue.toISOString().slice(0, 10)
}

function formatHours(value) {
  const hours = Number(value || 0)
  return Number.isInteger(hours) ? `${hours}` : hours.toFixed(1)
}

function formatDuration(minutes) {
  const hours = Number(minutes || 0) / 60
  return `${hours.toFixed(1)} hrs`
}

function formatRelativeDate(dateString) {
  if (!dateString) {
    return 'No recent entries'
  }

  const dateValue = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - dateValue.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays <= 0) {
    return 'Today'
  }
  if (diffDays === 1) {
    return '1 day ago'
  }
  return `${diffDays} days ago`
}

function formatDayLabel(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, { weekday: 'short' })
}

function formatChartDate(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })
}

function DashboardPage() {
  const [period, setPeriod] = useState('7d')
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(null)
  const [activity, setActivity] = useState([])
  const [previewEntries, setPreviewEntries] = useState([])
  const [projectActivity, setProjectActivity] = useState({ my_projects: [], owner_projects: [] })
  const [notifications, setNotifications] = useState([])

  // Transform activity data for recharts
  const chartData = useMemo(() => {
    return activity.map((point) => ({
      date: period === '30d'
        ? new Date(point.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
        : formatDayLabel(point.date),
      fullDate: formatChartDate(point.date),
      hours: Number(point.hours || 0),
      minutes: Number(point.minutes || 0),
    }))
  }, [activity, period])

  useEffect(() => {
    let isActive = true

    const load = async () => {
      setLoading(true)

      const now = new Date()
      const weekStart = startOfWeek(now)
      const monthStart = startOfMonth(now)

      const [
        summaryBaseResult,
        summaryWeekResult,
        summaryMonthResult,
        activityResult,
        previewResult,
        projectResult,
        notificationsResult,
      ] = await Promise.allSettled([
        getTimeSummary(),
        getTimeSummary({ start_date: toISODate(weekStart), end_date: toISODate(now) }),
        getTimeSummary({ start_date: toISODate(monthStart), end_date: toISODate(now) }),
        getDashboardActivity(period),
        getDashboardPreviewEntries(),
        getDashboardProjectActivity(),
        getNotificationsPreview(3),
      ])

      if (!isActive) return

      const summaryBase = summaryBaseResult.status === 'fulfilled' ? summaryBaseResult.value : null
      const summaryWeek = summaryWeekResult.status === 'fulfilled' ? summaryWeekResult.value : null
      const summaryMonth = summaryMonthResult.status === 'fulfilled' ? summaryMonthResult.value : null

      setSummary({
        hoursToday: Number(summaryBase?.hours_today ?? 0),
        hoursWeek: Number(summaryWeek?.total_hours ?? 0),
        hoursMonth: Number(summaryMonth?.total_hours ?? 0),
        entriesToday: Number(summaryBase?.entries_today ?? 0),
      })

      setActivity(
        activityResult.status === 'fulfilled' && Array.isArray(activityResult.value?.points)
          ? activityResult.value.points
          : [],
      )

      setPreviewEntries(
        previewResult.status === 'fulfilled' && Array.isArray(previewResult.value)
          ? previewResult.value
          : [],
      )

      setProjectActivity(
        projectResult.status === 'fulfilled' && projectResult.value
          ? projectResult.value
          : { my_projects: [], owner_projects: [] },
      )

      setNotifications(
        notificationsResult.status === 'fulfilled' && Array.isArray(notificationsResult.value)
          ? notificationsResult.value
          : [],
      )

      setLoading(false)
    }

    load()

    return () => {
      isActive = false
    }
  }, [period])

  return (
    <section className="dashboard-stack">
      <section className="dashboard-summary-row">
        <article className="summary-tile">
          <p className="summary-label">Hours Today</p>
          <p className="summary-value">{formatHours(summary?.hoursToday)} <span>hours</span></p>
        </article>
        <article className="summary-tile">
          <p className="summary-label">Hours This Week</p>
          <p className="summary-value">{formatHours(summary?.hoursWeek)} <span>hrs</span></p>
        </article>
        <article className="summary-tile">
          <p className="summary-label">Hours This Month</p>
          <p className="summary-value">{formatHours(summary?.hoursMonth)} <span>hrs</span></p>
        </article>
        <article className="summary-tile">
          <p className="summary-label">Entries Today</p>
          <p className="summary-value">{summary?.entriesToday ?? 0} <span>entry</span></p>
        </article>
      </section>

      <section className="dashboard-main-grid">
        <article className="dashboard-card chart-card">
          <div className="dashboard-card-head">
            <h2>Hours Worked Over Time</h2>
            <div className="period-toggle" role="tablist" aria-label="Activity period">
              <button
                type="button"
                className={period === '7d' ? 'active' : ''}
                onClick={() => setPeriod('7d')}
              >
                Last 7 Days
              </button>
              <button
                type="button"
                className={period === '30d' ? 'active' : ''}
                onClick={() => setPeriod('30d')}
              >
                Last 30 Days
              </button>
            </div>
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart
                data={chartData}
                margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e8eef8" />
                <XAxis 
                  dataKey="date"
                  angle={activity.length > 14 ? -45 : 0}
                  textAnchor={activity.length > 14 ? 'end' : 'middle'}
                  height={activity.length > 14 ? 60 : 30}
                  interval={activity.length > 14 ? 2 : 0}
                  tick={{ fontSize: 11 }}
                />
                <YAxis />
                <Tooltip 
                  cursor={{ fill: 'rgba(49, 121, 229, 0.1)' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="custom-tooltip">
                          <p className="tooltip-label">{data.fullDate}</p>
                          <p className="tooltip-value">{formatHours(data.hours)} hrs</p>
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Bar dataKey="hours" fill="#4f92f0" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="dashboard-card recent-card">
          <div className="dashboard-card-head">
            <h2>Recent Time Entries</h2>
          </div>
          {previewEntries.length === 0 ? (
            <p className="muted">No recent entries.</p>
          ) : (
            <ul className="recent-list">
              {previewEntries.map((entry) => (
                <li key={entry.id}>
                  <Link to={`/time-entries/${entry.id}`} className="recent-link">
                    <div className="recent-main">
                      <strong>{entry.title}</strong>
                      <p className="muted">{entry.description || 'No description'}</p>
                    </div>
                    <span className="recent-time">{formatDuration(entry.time)}</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>

      <section className="dashboard-bottom-grid">
        <article className="dashboard-card">
          <div className="dashboard-card-head">
            <h2>My Projects</h2>
          </div>
          {(projectActivity.my_projects || []).length === 0 ? (
            <p className="muted">No projects found.</p>
          ) : (
            <ul className="project-activity-list">
              {(projectActivity.my_projects || []).slice(0, 3).map((project) => (
                <li key={project.id}>
                  <Link to={`/projects/${project.id}`} className="project-link">
                    <div>
                      <strong>{project.name}</strong>
                      <p className="muted">{formatRelativeDate(project.last_entry_at)}</p>
                    </div>
                    <span className={`status-badge ${project.is_archived ? 'archived' : project.visibility?.toLowerCase()}`}>
                      {project.is_archived ? 'Archived' : project.visibility === 'PRIVATE' ? 'Private' : 'Public'}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="dashboard-card">
          <div className="dashboard-card-head">
            <h2>Owned Projects</h2>
          </div>
          {(projectActivity.owner_projects || []).length === 0 ? (
            <p className="muted">No owned projects found.</p>
          ) : (
            <ul className="project-activity-list">
              {(projectActivity.owner_projects || []).slice(0, 3).map((project) => (
                <li key={project.id}>
                  <Link to={`/projects/${project.id}`} className="project-link">
                    <div>
                      <strong>{project.name}</strong>
                      <p className="muted">{formatRelativeDate(project.last_entry_at)}</p>
                    </div>
                    <span className={`status-badge ${project.is_archived ? 'archived' : project.visibility?.toLowerCase()}`}>
                      {project.is_archived ? 'Archived' : project.visibility === 'PRIVATE' ? 'Private' : 'Public'}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </article>

        <article className="dashboard-card">
          <div className="dashboard-card-head">
            <h2>Notifications Preview</h2>
          </div>
          {notifications.length === 0 ? (
            <p className="muted">No notifications.</p>
          ) : (
            <ul className="notification-preview-list">
              {notifications.map((notification) => (
                <li key={notification.id}>
                  <p>{notification.message}</p>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>

      {loading ? <p className="muted">Loading dashboard...</p> : null}
    </section>
  )
}

export default DashboardPage
