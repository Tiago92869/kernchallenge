import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import ConfirmDeleteModal from '../components/ConfirmDeleteModal'
import NotificationDetailModal from '../components/NotificationDetailModal'
import { MOCK_NOTIFICATIONS } from '../mocks/notifications'

function formatRelativeTime(dateString) {
  const now = Date.now()
  const created = new Date(dateString).getTime()
  const diffMs = Math.max(0, now - created)
  const oneHour = 60 * 60 * 1000
  const oneDay = 24 * oneHour

  if (diffMs < oneDay) {
    if (diffMs < oneHour) {
      const minutes = Math.max(1, Math.floor(diffMs / (60 * 1000)))
      return `${minutes}m ago`
    }

    const hours = Math.floor(diffMs / oneHour)
    return `${hours}h ago`
  }

  if (diffMs < oneDay * 2) {
    return 'Yesterday'
  }

  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function NotificationsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [notifications, setNotifications] = useState(() => MOCK_NOTIFICATIONS.map((item) => ({ ...item })))
  const [searchValue, setSearchValue] = useState('')
  const [filterValue, setFilterValue] = useState('all')
  const [selectedId, setSelectedId] = useState(null)
  const [isMarkAllConfirmOpen, setIsMarkAllConfirmOpen] = useState(false)
  const openFromQuery = searchParams.get('open')
  const selectedNotificationId = selectedId || openFromQuery

  const counters = useMemo(() => {
    const unread = notifications.filter((item) => !item.isRead).length
    return {
      all: notifications.length,
      unread,
      read: notifications.length - unread,
    }
  }, [notifications])

  const visibleNotifications = useMemo(() => {
    const normalized = searchValue.trim().toLowerCase()

    return notifications
      .filter((item) => {
        if (filterValue === 'unread' && item.isRead) return false
        if (filterValue === 'read' && !item.isRead) return false
        if (!normalized) return true

        return [item.projectName, item.message, item.type, item.sender].join(' ').toLowerCase().includes(normalized)
      })
      .sort((left, right) => new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime())
  }, [notifications, searchValue, filterValue])

  const selectedNotification = notifications.find((item) => item.id === selectedNotificationId) || null

  function markAllAsRead() {
    setNotifications((current) => current.map((item) => ({ ...item, isRead: true })))
    setIsMarkAllConfirmOpen(false)
  }

  function openNotification(notificationId) {
    setNotifications((current) =>
      current.map((item) => (item.id === notificationId ? { ...item, isRead: true } : item)),
    )
    setSelectedId(notificationId)
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      next.set('open', notificationId)
      return next
    })
  }

  function closeNotification() {
    const activeId = selectedNotificationId
    if (activeId) {
      setNotifications((current) =>
        current.map((item) => (item.id === activeId ? { ...item, isRead: true } : item)),
      )
    }

    setSelectedId(null)
    setSearchParams((current) => {
      const next = new URLSearchParams(current)
      next.delete('open')
      return next
    })
  }

  return (
    <section className="stack-lg notifications-page">
      <div className="dashboard-card notifications-filters-card">
        <div className="notifications-actions-row">
          <button type="button" className="notifications-search-btn" aria-label="Search notifications">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M15.5 14h-.79l-.28-.27a6 6 0 1 0-.71.71l.27.28v.79L19 20.5 20.5 19zM10 14a4 4 0 1 1 0-8 4 4 0 0 1 0 8z" />
            </svg>
          </button>

          <label className="field notifications-search-field" htmlFor="notification-search">
            <span className="sr-only">Search notifications</span>
            <input
              id="notification-search"
              type="search"
              value={searchValue}
              onChange={(event) => setSearchValue(event.target.value)}
              placeholder="Search by message, project, sender, or type"
            />
          </label>

          <button type="button" className="btn-secondary" onClick={() => setIsMarkAllConfirmOpen(true)}>
            Mark all as read
          </button>
        </div>

        <div className="notifications-filter-tabs" role="tablist" aria-label="Notification status filter">
          <button
            type="button"
            className={`notifications-tab ${filterValue === 'all' ? 'active' : ''}`}
            onClick={() => setFilterValue('all')}
          >
            All ({counters.all})
          </button>
          <button
            type="button"
            className={`notifications-tab ${filterValue === 'unread' ? 'active' : ''}`}
            onClick={() => setFilterValue('unread')}
          >
            Unread ({counters.unread})
          </button>
          <button
            type="button"
            className={`notifications-tab ${filterValue === 'read' ? 'active' : ''}`}
            onClick={() => setFilterValue('read')}
          >
            Read ({counters.read})
          </button>
        </div>
      </div>

      <div className="dashboard-card notifications-list-card">
        {visibleNotifications.length ? (
          <ul className="notifications-list">
            {visibleNotifications.map((notification) => (
              <li key={notification.id}>
                <button
                  type="button"
                  className="notification-row"
                  onClick={() => openNotification(notification.id)}
                  title="Open notification"
                >
                  <span
                    className={`notification-read-indicator ${notification.isRead || notification.id === selectedNotificationId ? 'read' : 'unread'}`}
                    aria-label={notification.isRead || notification.id === selectedNotificationId ? 'Read notification' : 'Unread notification'}
                  />

                  <span className="notification-content">
                    <strong>{notification.projectName}</strong>
                    <span>{notification.message}</span>
                  </span>

                  <span className="notification-time">{formatRelativeTime(notification.createdAt)}</span>
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <div className="entries-empty-state">
            <h3>No notifications match the current filters</h3>
            <p className="muted">Try changing search text or selecting a different notification status filter.</p>
          </div>
        )}
      </div>

      <NotificationDetailModal notification={selectedNotification} onClose={closeNotification} />

      <ConfirmDeleteModal
        isOpen={isMarkAllConfirmOpen}
        onCancel={() => setIsMarkAllConfirmOpen(false)}
        onConfirm={markAllAsRead}
        title="Mark All As Read"
        message="Are you sure you want to mark all messages as read?"
        confirmText="Yes, mark all"
        cancelText="No"
        confirmClassName="btn-primary"
      />
    </section>
  )
}

export default NotificationsPage
