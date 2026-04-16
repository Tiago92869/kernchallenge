import { Link } from 'react-router-dom'

function NotFoundPage() {
  return (
    <section className="page stack-lg">
      <h1>Page Not Found</h1>
      <p className="muted">The route you requested does not exist.</p>
      <Link to="/dashboard">Go to dashboard</Link>
    </section>
  )
}

export default NotFoundPage
