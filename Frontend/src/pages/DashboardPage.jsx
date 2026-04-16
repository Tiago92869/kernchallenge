import { Link } from 'react-router-dom'

function DashboardPage() {
  return (
    <section className="stack-lg">
      <h1>Dashboard</h1>
      <p className="muted">Frontend scaffold is ready. Start wiring backend endpoints page by page.</p>
      <div className="grid-3">
        <article className="card stack-sm">
          <h2>Projects</h2>
          <p className="muted">Integrate project activity and project listing endpoints.</p>
          <Link to="/projects">Open Projects</Link>
        </article>
        <article className="card stack-sm">
          <h2>Time Entries</h2>
          <p className="muted">Integrate summary, dashboard chart, and preview endpoints.</p>
          <Link to="/time-entries">Open Time Entries</Link>
        </article>
        <article className="card stack-sm">
          <h2>Notifications</h2>
          <p className="muted">Integrate recipient notifications endpoint with filters.</p>
          <Link to="/notifications">Open Notifications</Link>
        </article>
      </div>
    </section>
  )
}

export default DashboardPage
