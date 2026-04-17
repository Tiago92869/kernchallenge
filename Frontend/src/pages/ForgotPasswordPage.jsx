import { Link } from 'react-router-dom'

import logoImage from '../../../Documentation/images/logo.png'

function ForgotPasswordPage() {
  return (
    <main className="app-frame">
      <section className="login-shell">
        <section className="login-panel">
          <div className="login-card stack-sm">
            <Link to="/" className="brand-mark login-brand" aria-label="TimeSync home">
              <img src={logoImage} className="brand-logo login-logo" alt="TimeSync" />
            </Link>
            <h1 className="login-title">Forgot password</h1>
            <p className="muted-text">
              Password recovery is not connected yet. This page is here so users can navigate to the recovery flow.
            </p>
            <Link to="/login" className="inline-link">Back to login</Link>
          </div>
        </section>
      </section>
    </main>
  )
}

export default ForgotPasswordPage
