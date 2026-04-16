import { useMemo, useState } from 'react'

const MOCK_PROJECTS = [
  {
    id: 101,
    name: 'Apollo Redesign',
    client: 'Northwind',
    status: 'active',
    isMine: true,
    members: 5,
    progress: 62,
    updatedAt: '2026-04-14T10:10:00Z',
  },
  {
    id: 102,
    name: 'Payroll API Migration',
    client: 'Contoso',
    status: 'active',
    isMine: true,
    members: 3,
    progress: 83,
    updatedAt: '2026-04-15T08:20:00Z',
  },
  {
    id: 103,
    name: 'Onboarding Portal',
    client: 'Adventure Works',
    status: 'archived',
    isMine: false,
    members: 6,
    progress: 100,
    updatedAt: '2026-03-30T16:00:00Z',
  },
  {
    id: 104,
    name: 'Mobile Timesheet MVP',
    client: 'Fabrikam',
    status: 'active',
    isMine: false,
    members: 4,
    progress: 29,
    updatedAt: '2026-04-12T11:45:00Z',
  },
  {
    id: 105,
    name: 'Executive Reporting',
    client: 'Tailspin',
    status: 'paused',
    isMine: true,
    members: 2,
    progress: 44,
    updatedAt: '2026-04-07T09:00:00Z',
  },
]

function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function ProjectsPage() {
  const [scenario, setScenario] = useState('normal')
  const [search, setSearch] = useState('')
  const [scope, setScope] = useState('all')
  const [sortBy, setSortBy] = useState('recent')

  const baseProjects = useMemo(() => {
    if (scenario === 'empty') {
      return []
    }
    return MOCK_PROJECTS
  }, [scenario])

  const visibleProjects = useMemo(() => {
    const searchTerm = search.trim().toLowerCase()

    let items = baseProjects.filter((project) => {
      if (scope === 'mine' && !project.isMine) {
        return false
      }
      if (scope === 'active' && project.status !== 'active') {
        return false
      }
      if (scope === 'archived' && project.status !== 'archived') {
        return false
      }
      if (!searchTerm) {
        return true
      }
      return (
        project.name.toLowerCase().includes(searchTerm) ||
        project.client.toLowerCase().includes(searchTerm)
      )
    })

    items = [...items]
    items.sort((a, b) => {
      if (sortBy === 'name') {
        return a.name.localeCompare(b.name)
      }
      if (sortBy === 'progress') {
        return b.progress - a.progress
      }
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    })

    return items
  }, [baseProjects, scope, search, sortBy])

  const stats = useMemo(() => {
    const total = baseProjects.length
    const active = baseProjects.filter((project) => project.status === 'active').length
    const mine = baseProjects.filter((project) => project.isMine).length
    const archived = baseProjects.filter((project) => project.status === 'archived').length
    return { total, active, mine, archived }
  }, [baseProjects])

  return (
    <section className="stack-lg">
      <div className="page-head">
        <h1>Projects</h1>
        <p className="muted">Mocked list to validate page behavior before API integration.</p>
      </div>

      <div className="card stack-sm">
        <strong>Scenario</strong>
        <div className="pill-row">
          <button
            type="button"
            className={scenario === 'normal' ? 'btn' : 'btn ghost'}
            onClick={() => setScenario('normal')}
          >
            Normal
          </button>
          <button
            type="button"
            className={scenario === 'loading' ? 'btn' : 'btn ghost'}
            onClick={() => setScenario('loading')}
          >
            Loading
          </button>
          <button
            type="button"
            className={scenario === 'empty' ? 'btn' : 'btn ghost'}
            onClick={() => setScenario('empty')}
          >
            Empty
          </button>
          <button
            type="button"
            className={scenario === 'error' ? 'btn' : 'btn ghost'}
            onClick={() => setScenario('error')}
          >
            Error
          </button>
        </div>
      </div>

      <div className="grid-4">
        <article className="card stat-card">
          <span className="muted">Total</span>
          <strong>{stats.total}</strong>
        </article>
        <article className="card stat-card">
          <span className="muted">Active</span>
          <strong>{stats.active}</strong>
        </article>
        <article className="card stat-card">
          <span className="muted">Mine</span>
          <strong>{stats.mine}</strong>
        </article>
        <article className="card stat-card">
          <span className="muted">Archived</span>
          <strong>{stats.archived}</strong>
        </article>
      </div>

      <div className="card controls-grid">
        <label className="field">
          Search
          <input
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by project or client"
          />
        </label>

        <label className="field">
          Scope
          <select value={scope} onChange={(event) => setScope(event.target.value)}>
            <option value="all">All projects</option>
            <option value="mine">My projects</option>
            <option value="active">Active only</option>
            <option value="archived">Archived only</option>
          </select>
        </label>

        <label className="field">
          Sort by
          <select value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
            <option value="recent">Most recent</option>
            <option value="name">Name (A-Z)</option>
            <option value="progress">Progress (high first)</option>
          </select>
        </label>
      </div>

      {scenario === 'loading' && (
        <div className="card">
          <p className="muted">Loading projects...</p>
        </div>
      )}

      {scenario === 'error' && (
        <div className="card">
          <p className="error">Failed to load projects. Mocked error state for UI testing.</p>
        </div>
      )}

      {scenario === 'normal' && (
        <div className="stack-sm">
          {visibleProjects.length === 0 ? (
            <div className="card">
              <p className="muted">No projects match the current filters.</p>
            </div>
          ) : (
            visibleProjects.map((project) => (
              <article key={project.id} className="card project-item">
                <div>
                  <h2>{project.name}</h2>
                  <p className="muted">{project.client}</p>
                </div>
                <div className="project-meta">
                  <span className={`tag ${project.status}`}>{project.status}</span>
                  <span>{project.members} members</span>
                  <span>{project.progress}% complete</span>
                  <span>Updated {formatDate(project.updatedAt)}</span>
                </div>
              </article>
            ))
          )}
        </div>
      )}

      {scenario === 'empty' && (
        <div className="card">
          <p className="muted">No projects yet. Mocked empty state for first-time users.</p>
        </div>
      )}
    </section>
  )
}

export default ProjectsPage
