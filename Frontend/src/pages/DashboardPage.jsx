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
  getProjectsList,
  getTimeEntriesList,
  getTimeSummary,
} from '../services/dashboardService'

const FALLBACK = {
  summary: {
    hoursToday: 0,
    hoursWeek: 12.5,
    hoursMonth: 38.0,
    entriesToday: 1,
  },
  preview: [
    { id: '1', day: 24, title: 'Project Delta', description: 'Organized meeting notes', time: 90 },
    { id: '2', day: 23, title: 'Project Alpha', description: 'Wrote new landing page copy', time: 150 },
    { id: '3', day: 23, title: 'Project Alpha', description: 'Team meeting and follow-ups', time: 60 },
    { id: '4', day: 22, title: 'Project Beta', description: 'Resolved ticket #345', time: 30 },
    { id: '5', day: 21, title: 'Project Gamma', description: 'Reviewed QA issues', time: 75 },
    { id: '6', day: 20, title: 'Project Delta', description: 'Prepared sprint handoff', time: 45 },
  ],
  projects: {
    my_projects: [
      {
        id: 'm1',
        name: 'Beta Website Update',
        visibility: 'PUBLIC',
        is_archived: false,
        last_entry_at: '2026-04-15T10:10:00',
      },
      {
        id: 'm2',
        name: 'Marketing Campaign',
        visibility: 'PRIVATE',
        is_archived: false,
        last_entry_at: '2026-04-14T08:20:00',
      },
      {
        id: 'm3',
        name: 'Website Redesign',
        visibility: 'PUBLIC',
        is_archived: true,
        last_entry_at: '2026-04-03T12:00:00',
      },
    ],
    owner_projects: [
      {
        id: 'o1',
        name: 'Project Alpha',
        visibility: 'PUBLIC',
        is_archived: false,
        last_entry_at: '2026-04-16T09:10:00',
      },
      {
        id: 'o2',
        name: 'Mobile App Development',
        visibility: 'PRIVATE',
        is_archived: false,
        last_entry_at: '2026-04-15T08:40:00',
      },
      {
        id: 'o3',
        name: 'Website Redesign',
        visibility: 'PUBLIC',
        is_archived: true,
        last_entry_at: '2026-04-03T12:00:00',
      },
    ],
  },
  notifications: [
    {
      id: 'n1',
      message: 'You were added to Project Alpha',
      created_at: '2026-04-16T11:20:00',
    },
    {
      id: 'n2',
      message: 'New project Marketing Campaign created',
      created_at: '2026-04-15T10:15:00',
    },
  ],
}

function buildFallbackActivity(period) {
  const days = period === '30d' ? 30 : 7
  const today = new Date()
  const points = []

  for (let index = days - 1; index >= 0; index -= 1) {
    const itemDate = new Date(today)
    itemDate.setDate(today.getDate() - index)
    
    let hours
    if (period === '30d') {
      // 30-day pattern: more varied with weekly cycles
      const wave = Math.sin((days - index) / 3.5)
      const weekCycle = Math.sin(((days - index) % 7) / 3.5)
      hours = Math.max(0.5, Number((3.2 + wave * 2.1 + weekCycle * 1.8 + Math.random() * 0.5).toFixed(2)))
    } else {
      // 7-day pattern: consistent wave
      const wave = Math.sin((days - index) / 2.2)
      hours = Math.max(0.5, Number((2.8 + wave * 1.9 + (index % 5) * 0.18).toFixed(2)))
    }

    points.push({
      date: itemDate.toISOString().slice(0, 10),
      hours,
      minutes: Math.round(hours * 60),
    })
  }

  return points
}

function toRecentFromEntries(entries, projectMap) {
  return entries.slice(0, 6).map((entry) => {
    const projectName = projectMap.get(entry.project_id) || 'Project'
    return {
      id: entry.id,
      day: new Date(entry.date).getDate(),
      title: projectName,
      description: entry.description || 'No description',
      time: Number(entry.hours || 0),
    }
  })
}

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
  const [apiWarning, setApiWarning] = useState('')
  const [summary, setSummary] = useState(FALLBACK.summary)
  const [activity, setActivity] = useState(() => buildFallbackActivity('7d'))
  const [previewEntries, setPreviewEntries] = useState(FALLBACK.preview)
  const [projectActivity, setProjectActivity] = useState(FALLBACK.projects)
  const [notifications, setNotifications] = useState(FALLBACK.notifications)

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
      setApiWarning('')

      // Short-circuit: bypass token means no real backend — go straight to fallback
      const token = localStorage.getItem('auth_token')
      if (token === 'dev-bypass-token') {
        if (!isActive) return
        setActivity(buildFallbackActivity(period))
        setApiWarning('Using preview data. Re-enable real login to load backend data.')
        setLoading(false)
        return
      }

      const now = new Date()
      const weekStart = startOfWeek(now)
      const monthStart = startOfMonth(now)

      const [
        summaryBaseResult,
        summaryWeekResult,
        summaryMonthResult,
        activityResult,
        previewResult,
        entriesResult,
        projectsResult,
        projectResult,
        notificationsResult,
      ] = await Promise.allSettled([
        getTimeSummary(),
        getTimeSummary({ start_date: toISODate(weekStart), end_date: toISODate(now) }),
        getTimeSummary({ start_date: toISODate(monthStart), end_date: toISODate(now) }),
        getDashboardActivity(period),
        getDashboardPreviewEntries(),
        getTimeEntriesList(),
        getProjectsList(),
        getDashboardProjectActivity(),
        getNotificationsPreview(3),
      ])

      if (!isActive) {
        return
      }

      const usingFallback = [
        summaryBaseResult,
        summaryWeekResult,
        summaryMonthResult,
        activityResult,
        previewResult,
        entriesResult,
        projectsResult,
        projectResult,
        notificationsResult,
      ].some((result) => result.status === 'rejected')

      if (usingFallback) {
        setApiWarning('Some dashboard sections are using preview data. Re-enable real login to load backend data.')
      }

      const summaryBase = summaryBaseResult.status === 'fulfilled' ? summaryBaseResult.value : null
      const summaryWeek = summaryWeekResult.status === 'fulfilled' ? summaryWeekResult.value : null
      const summaryMonth = summaryMonthResult.status === 'fulfilled' ? summaryMonthResult.value : null

      setSummary({
        hoursToday: Number(summaryBase?.hours_today ?? FALLBACK.summary.hoursToday),
        hoursWeek: Number(summaryWeek?.total_hours ?? FALLBACK.summary.hoursWeek),
        hoursMonth: Number(summaryMonth?.total_hours ?? FALLBACK.summary.hoursMonth),
        entriesToday: Number(summaryBase?.entries_today ?? FALLBACK.summary.entriesToday),
      })

      const minExpectedPoints = period === '30d' ? 20 : 4
      const apiPoints = activityResult.status === 'fulfilled' && Array.isArray(activityResult.value?.points)
        ? activityResult.value.points
        : []
      
      const nextActivity = apiPoints.length >= minExpectedPoints ? apiPoints : buildFallbackActivity(period)
      setActivity(nextActivity)

      const projectsMap = new Map(
        projectsResult.status === 'fulfilled'
          ? projectsResult.value.map((project) => [project.id, project.name])
          : [],
      )

      const recentFromEntries =
        entriesResult.status === 'fulfilled' && entriesResult.value.length
          ? toRecentFromEntries(entriesResult.value, projectsMap)
          : []

      const recentFromPreview =
        previewResult.status === 'fulfilled' && Array.isArray(previewResult.value)
          ? previewResult.value
          : []

      const combinedRecent = (recentFromEntries.length ? recentFromEntries : recentFromPreview).slice(0, 6)
      setPreviewEntries(combinedRecent.length ? combinedRecent : FALLBACK.preview)

      setProjectActivity(
        projectResult.status === 'fulfilled' && projectResult.value
          ? projectResult.value
          : FALLBACK.projects,
      )

      setNotifications(
        notificationsResult.status === 'fulfilled' && Array.isArray(notificationsResult.value)
          ? notificationsResult.value
          : FALLBACK.notifications,
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
      {apiWarning ? <p className="muted dashboard-warning">{apiWarning}</p> : null}

      <section className="dashboard-summary-row">
        <article className="summary-tile">
          <p className="summary-label">Hours Today</p>
          <p className="summary-value">{formatHours(summary.hoursToday)} <span>hours</span></p>
        </article>
        <article className="summary-tile">
          <p className="summary-label">Hours This Week</p>
          <p className="summary-value">{formatHours(summary.hoursWeek)} <span>hrs</span></p>
        </article>
        <article className="summary-tile">
          <p className="summary-label">Hours This Month</p>
          <p className="summary-value">{formatHours(summary.hoursMonth)} <span>hrs</span></p>
        </article>
        <article className="summary-tile">
          <p className="summary-label">Entries Today</p>
          <p className="summary-value">{summary.entriesToday} <span>entry</span></p>
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
        </article>
      </section>

      <section className="dashboard-bottom-grid">
        <article className="dashboard-card">
          <div className="dashboard-card-head">
            <h2>My Projects</h2>
          </div>
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
        </article>

        <article className="dashboard-card">
          <div className="dashboard-card-head">
            <h2>Owned Projects</h2>
          </div>
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
        </article>

        <article className="dashboard-card">
          <div className="dashboard-card-head">
            <h2>Notifications Preview</h2>
          </div>
          <ul className="notification-preview-list">
            {notifications.map((notification) => (
              <li key={notification.id}>
                <p>{notification.message}</p>
              </li>
            ))}
          </ul>
        </article>
      </section>

      {loading ? <p className="muted">Loading dashboard...</p> : null}
    </section>
  )
}

export default DashboardPage
