import { Link } from 'react-router-dom'

import heroImage from '../../../Documentation/images/land_page_image.png'
import logoImage from '../../../Documentation/images/logo.png'

function LandingPage() {
  return (
    <main className="app-frame">
      <section className="landing-shell">
        <header className="landing-header">
          <Link to="/" className="brand-mark" aria-label="TimeSync home">
            <img src={logoImage} className="brand-logo" alt="TimeSync" />
          </Link>

          <nav className="public-nav" aria-label="Public actions">
            <Link to="/login" className="public-link">
              Login
            </Link>
            <Link to="/signup" className="btn-primary">
              Sign Up
            </Link>
          </nav>
        </header>
 
        <section className="hero-panel">
          <div className="hero-copy">
            <h1>Streamline Your Time Tracking</h1>
            <p>
              Track work hours, manage projects and boost your team productivity
              with TimeSync.
            </p>
            <Link to="/signup" className="btn-primary hero-cta">
              Create Account
            </Link>
          </div>
 
          <div className="hero-visual-wrap" aria-hidden="true">
            <img
              src={heroImage}
              className="hero-visual"
              alt=""
              loading="eager"
              decoding="async"
            />
          </div>
        </section>
       </section>
     </main>
   )
 }
 
 export default LandingPage
