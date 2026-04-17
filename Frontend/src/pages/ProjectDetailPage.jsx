import { Link, useParams } from 'react-router-dom'

const MOCK_PROJECTS = {
  m1: { id: 'm1', name: 'Beta Website Update', visibility: 'PUBLIC', is_archived: false, last_entry_at: '2026-04-15T10:10:00', description: 'Revamping the main marketing website with a fresh design and improved performance.' },
  m2: { id: 'm2', name: 'Marketing Campaign', visibility: 'PRIVATE', is_archived: false, last_entry_at: '2026-04-14T08:20:00', description: 'Q2 marketing push across social media and email channels.' },
  m3: { id: 'm3', name: 'Website Redesign', visibility: 'PUBLIC', is_archived: true, last_entry_at: '2026-04-03T12:00:00', description: 'Full redesign of the corporate website. Project is now archived.' },
  o1: { id: 'o1', name: 'Project Alpha', visibility: 'PUBLIC', is_archived: false, last_entry_at: '2026-04-16T09:10:00', description: 'Core product development initiative for the new platform launch.' },
  o2: { id: 'o2', name: 'Mobile App Development', visibility: 'PRIVATE', is_archived: false, last_entry_at: '2026-04-15T08:40:00', description: 'Native iOS and Android app for the main product.' },
  o3: { id: 'o3', name: 'Website Redesign', visibility: 'PUBLIC', is_archived: true, last_entry_at: '2026-04-03T12:00:00', description: 'Corporate website redesign. Archived.' },
}

function ProjectDetailPage() {
  const { id } = useParams()
  const project = MOCK_PROJECTS[id]

  if (!project) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Project not found.</p>
          <Link to="/projects" className="btn-primary" style={{ marginTop: '12px', display: 'inline-block' }}>Back to Projects</Link>
        </div>
      </section>
    )
  }

  return (
    <section className="dashboard-stack">
      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>{project.name}</h2>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span className={`status-badge ${project.is_archived ? 'archived' : project.visibility?.toLowerCase()}`}>
              {project.is_archived ? 'Archived' : project.visibility === 'PRIVATE' ? 'Private' : 'Public'}
            </span>
            <Link to="/projects" className="btn-secondary">← Back</Link>
          </div>
        </div>
        <div className="profile-details-grid" style={{ marginTop: '16px' }}>
          <div className="profile-field">
            <label>Description</label>
            <p>{project.description}</p>
          </div>
          <div className="profile-field">
            <label>Visibility</label>
            <p>{project.visibility === 'PRIVATE' ? 'Private' : 'Public'}</p>
          </div>
          <div className="profile-field">
            <label>Status</label>
            <p>{project.is_archived ? 'Archived' : 'Active'}</p>
          </div>
          <div className="profile-field">
            <label>Last Activity</label>
            <p>{new Date(project.last_entry_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default ProjectDetailPage
