import { Link, useParams } from 'react-router-dom'

const MOCK_ENTRIES = {
  1: { id: '1', title: 'Project Delta', description: 'Organized meeting notes', date: '2026-04-24', hours: 1.5, project: 'Project Delta' },
  2: { id: '2', title: 'Project Alpha', description: 'Wrote new landing page copy', date: '2026-04-23', hours: 2.5, project: 'Project Alpha' },
  3: { id: '3', title: 'Project Alpha', description: 'Team meeting and follow-ups', date: '2026-04-23', hours: 1.0, project: 'Project Alpha' },
  4: { id: '4', title: 'Project Beta', description: 'Resolved ticket #345', date: '2026-04-22', hours: 0.5, project: 'Project Beta' },
  5: { id: '5', title: 'Project Gamma', description: 'Reviewed QA issues', date: '2026-04-21', hours: 1.25, project: 'Project Gamma' },
  6: { id: '6', title: 'Project Delta', description: 'Prepared sprint handoff', date: '2026-04-20', hours: 0.75, project: 'Project Delta' },
}

function TimeEntryDetailPage() {
  const { id } = useParams()
  const entry = MOCK_ENTRIES[id]

  if (!entry) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Time entry not found.</p>
          <Link to="/time-entries" className="btn-primary" style={{ marginTop: '12px', display: 'inline-block' }}>Back to Entries</Link>
        </div>
      </section>
    )
  }

  return (
    <section className="dashboard-stack">
      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>{entry.title}</h2>
          <Link to="/time-entries" className="btn-secondary">← Back</Link>
        </div>
        <div className="profile-details-grid" style={{ marginTop: '16px' }}>
          <div className="profile-field">
            <label>Project</label>
            <p>{entry.project}</p>
          </div>
          <div className="profile-field">
            <label>Date</label>
            <p>{new Date(entry.date).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
          </div>
          <div className="profile-field">
            <label>Hours Logged</label>
            <p>{entry.hours} hrs</p>
          </div>
          <div className="profile-field">
            <label>Description</label>
            <p>{entry.description}</p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default TimeEntryDetailPage
