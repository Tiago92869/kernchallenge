function UserProfilePage() {
  return (
    <section className="profile-page">
      <div className="dashboard-card profile-card">
        <div className="profile-avatar-large" aria-hidden="true">A</div>
        <div className="profile-info">
          <h2>Alex Johnson</h2>
          <p className="muted">alex.johnson@example.com</p>
          <span className="status-badge public">Active</span>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>Account Details</h2>
        </div>
        <div className="profile-details-grid">
          <div className="profile-field">
            <label>First Name</label>
            <p>Alex</p>
          </div>
          <div className="profile-field">
            <label>Last Name</label>
            <p>Johnson</p>
          </div>
          <div className="profile-field">
            <label>Email</label>
            <p>alex.johnson@example.com</p>
          </div>
          <div className="profile-field">
            <label>Member Since</label>
            <p>January 2026</p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default UserProfilePage
