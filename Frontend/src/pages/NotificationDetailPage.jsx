import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { getNotifications, markNotificationRead } from '../services/notificationService'

function formatDateTime(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatType(value) {
  return (value || '').replaceAll('_', ' ')
}

function NotificationDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [notification, setNotification] = useState(null)

  useEffect(() => {
    let isActive = true

    const load = async () => {
      setLoading(true)
      try {
        const items = await getNotifications()
        if (!isActive) return

        const selected = items.find((item) => item.id === id) || null
        setNotification(selected)

        if (selected && !selected.is_read) {
          setNotification((current) => (current ? { ...current, is_read: true } : current))
          markNotificationRead(selected.id).catch(() => {})
        }
      } finally {
        if (isActive) {
          setLoading(false)
        }
      }
    }

    load()

    return () => {
      isActive = false
    }
  }, [id])

  const statusText = useMemo(() => (notification?.is_read ? 'Read' : 'Unread'), [notification])

  if (loading) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Loading notification...</p>
        </div>
      </section>
    )
  }

  if (!notification) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card stack-sm">
          <p className="muted">Notification not found.</p>
          <button type="button" className="btn-primary entry-missing-link" onClick={() => navigate('/notifications')}>
            Back to Notifications
          </button>
        </div>
      </section>
    )
  }

  return (
    <section className="dashboard-stack">
      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>Notification Details</h2>
          <Link to="/notifications" className="btn-secondary" style={{ textDecoration: 'none' }}>
            View All
          </Link>
        </div>

        <div className="profile-details-grid">
          <div className="profile-field">
            <label>Type</label>
            <p>{formatType(notification.notification_type) || '-'}</p>
          </div>
          <div className="profile-field">
            <label>Status</label>
            <p>{statusText}</p>
          </div>
          <div className="profile-field">
            <label>Created At</label>
            <p>{formatDateTime(notification.created_at)}</p>
          </div>
          <div className="profile-field">
            <label>Read At</label>
            <p>{formatDateTime(notification.read_at)}</p>
          </div>
          <div className="profile-field">
            <label>Project Id</label>
            <p>{notification.project_id || '-'}</p>
          </div>
          <div className="profile-field">
            <label>Actor User Id</label>
            <p>{notification.actor_user_id || '-'}</p>
          </div>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="dashboard-card-head">
          <h2>Message</h2>
        </div>
        <p className="entry-detail-description">{notification.message || '-'}</p>
      </div>
    </section>
  )
}

export default NotificationDetailPage
