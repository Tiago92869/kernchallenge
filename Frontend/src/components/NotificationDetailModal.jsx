function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function NotificationDetailModal({ notification, onClose }) {
  if (!notification) {
    return null
  }

  return (
    <div className="modal-overlay" role="presentation" onClick={onClose}>
      <article
        className="modal-card notification-detail-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="notification-detail-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-head">
          <h2 id="notification-detail-title">
            {notification.notification_type?.replaceAll('_', ' ')}
          </h2>
          <button type="button" className="notification-close-btn" onClick={onClose} aria-label="Close notification">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M18.3 5.7 12 12l6.3 6.3-1.4 1.4L10.6 13.4 4.3 19.7 2.9 18.3 9.2 12 2.9 5.7l1.4-1.4 6.3 6.3 6.3-6.3z" />
            </svg>
          </button>
        </header>

        <div className="modal-body notification-detail-body">
          <section className="notification-message-hero">
            <p>{notification.message}</p>
          </section>

          <div className="profile-details-grid">
            <div className="profile-field">
              <label>Type</label>
              <p>{notification.notification_type?.replaceAll('_', ' ')}</p>
            </div>
            <div className="profile-field">
              <label>Status</label>
              <p>{notification.is_read ? 'Read' : 'Unread'}</p>
            </div>
            <div className="profile-field">
              <label>Created</label>
              <p>{formatDateTime(notification.created_at)}</p>
            </div>
            {notification.read_at ? (
              <div className="profile-field">
                <label>Read at</label>
                <p>{formatDateTime(notification.read_at)}</p>
              </div>
            ) : null}
          </div>
        </div>
      </article>
    </div>
  )
}

export default NotificationDetailModal
